/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */

package org.opensearch.knn.index.query;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.Setter;
import lombok.extern.log4j.Log4j2;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.FieldExistsQuery;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.QueryVisitor;
import org.apache.lucene.search.ScoreMode;
import org.apache.lucene.search.Weight;
import org.apache.lucene.search.join.BitSetProducer;
import org.opensearch.common.StopWatch;
import org.opensearch.knn.index.VectorDataType;
import org.opensearch.knn.index.query.memoryoptsearch.MemoryOptimizedKNNWeight;
import org.opensearch.knn.index.query.rescore.RescoreContext;
import org.opensearch.knn.profile.KNNProfileUtil;
import org.opensearch.knn.profile.ProfileDefaultKNNWeight;
import org.opensearch.knn.profile.ProfileMemoryOptKNNWeight;
import org.opensearch.search.profile.ContextualProfileBreakdown;
import org.opensearch.search.profile.query.QueryProfiler;

import java.io.IOException;
import java.util.Arrays;
import java.util.Map;
import java.util.Objects;

/**
 * Custom KNN query. Query is used for KNNEngine's that create their own custom segment files. These files need to be
 * loaded and queried in a custom manner throughout the query path.
 */
@Log4j2
@Getter
@Builder
@AllArgsConstructor
public class KNNQuery extends Query {

    private final String field;
    private final float[] queryVector;
    private final byte[] byteQueryVector;
    private int k;
    private Map<String, ?> methodParameters;
    private final String indexName;
    private final VectorDataType vectorDataType;
    private final RescoreContext rescoreContext;
    @Setter
    private Query filterQuery;
    @Getter
    private BitSetProducer parentsFilter;
    private Float radius;
    private Context context;
    @Setter
    @Getter
    private boolean explain;
    private boolean isMemoryOptimizedSearch;

    // Note: ideally query should not have to deal with shard level information. Adding it for logging purposes only
    // TODO: ThreadContext does not work with logger, remove this from here once its figured out
    private int shardId;

    public KNNQuery(
        final String field,
        final float[] queryVector,
        final int k,
        final String indexName,
        final BitSetProducer parentsFilter
    ) {
        this(field, queryVector, null, k, indexName, null, parentsFilter, VectorDataType.FLOAT, null);
    }

    public KNNQuery(
        final String field,
        final float[] queryVector,
        final int k,
        final String indexName,
        final Query filterQuery,
        final BitSetProducer parentsFilter,
        final RescoreContext rescoreContext
    ) {
        this(field, queryVector, null, k, indexName, filterQuery, parentsFilter, VectorDataType.FLOAT, rescoreContext);
    }

    public KNNQuery(
        final String field,
        final byte[] byteQueryVector,
        final int k,
        final String indexName,
        final Query filterQuery,
        final BitSetProducer parentsFilter,
        final VectorDataType vectorDataType,
        final RescoreContext rescoreContext
    ) {
        this(field, null, byteQueryVector, k, indexName, filterQuery, parentsFilter, vectorDataType, rescoreContext);
    }

    private KNNQuery(
        final String field,
        final float[] queryVector,
        final byte[] byteQueryVector,
        final int k,
        final String indexName,
        final Query filterQuery,
        final BitSetProducer parentsFilter,
        final VectorDataType vectorDataType,
        final RescoreContext rescoreContext
    ) {
        this.field = field;
        this.queryVector = queryVector;
        this.byteQueryVector = byteQueryVector;
        this.k = k;
        this.indexName = indexName;
        this.filterQuery = filterQuery;
        this.parentsFilter = parentsFilter;
        this.vectorDataType = vectorDataType;
        this.rescoreContext = rescoreContext;
    }

    /**
     * Constructor for KNNQuery with query vector, index name and parent filter
     *
     * @param field field name
     * @param queryVector query vector
     * @param indexName index name
     * @param parentsFilter parent filter
     */
    public KNNQuery(String field, float[] queryVector, String indexName, BitSetProducer parentsFilter) {
        this(field, queryVector, null, 0, indexName, null, parentsFilter, VectorDataType.FLOAT, null);
    }

    /**
     * Constructor for KNNQuery with radius
     *
     * @param radius engine radius
     * @return KNNQuery
     */
    public KNNQuery radius(Float radius) {
        this.radius = radius;
        return this;
    }

    /**
     * Constructor for KNNQuery with Context
     *
     * @param context Context for KNNQuery
     * @return KNNQuery
     */
    public KNNQuery kNNQueryContext(Context context) {
        this.context = context;
        return this;
    }

    /**
     * Constructor for KNNQuery with filter query
     *
     * @param filterQuery filter query
     * @return KNNQuery
     */
    public KNNQuery filterQuery(Query filterQuery) {
        this.filterQuery = filterQuery;
        return this;
    }

    /**
     * Constructs Weight implementation for this query
     *
     * @param searcher  searcher for given segment
     * @param scoreMode  How the produced scorers will be consumed.
     * @param boost     The boost that is propagated by the parent queries.
     * @return Weight   For calculating scores
     */
    @Override
    public Weight createWeight(IndexSearcher searcher, ScoreMode scoreMode, float boost) throws IOException {
        StopWatch stopWatch = null;
        if (log.isDebugEnabled()) {
            stopWatch = new StopWatch().start();
        }

        final Weight filterWeight = getFilterWeight(searcher);
        if (log.isDebugEnabled() && stopWatch != null) {
            stopWatch.stop();
            log.debug(
                "Creating filter weight, Shard: [{}], field: [{}] took in nanos: [{}]",
                shardId,
                field,
                stopWatch.totalTime().nanos()
            );
        }

        QueryProfiler profiler = KNNProfileUtil.getProfiler(searcher);
        if (profiler != null) {
            ContextualProfileBreakdown profile = (ContextualProfileBreakdown) profiler.getProfileBreakdown(this);
            if (isMemoryOptimizedSearch) {
                return new ProfileMemoryOptKNNWeight(this, boost, filterWeight, searcher, k, profile);
            }
            return new ProfileDefaultKNNWeight(this, boost, filterWeight, profile);
        }

        if (isMemoryOptimizedSearch) {
            // Using memory optimized search logic on index.
            return new MemoryOptimizedKNNWeight(this, boost, filterWeight, searcher, k);
        }

        // Using native library to perform search on index.
        return new DefaultKNNWeight(this, boost, filterWeight);
    }

    private Weight getFilterWeight(IndexSearcher searcher) throws IOException {
        if (this.getFilterQuery() != null) {
            // Run the filter query
            final BooleanQuery booleanQuery = new BooleanQuery.Builder().add(this.getFilterQuery(), BooleanClause.Occur.FILTER)
                .add(new FieldExistsQuery(this.getField()), BooleanClause.Occur.FILTER)
                .build();
            final Query rewritten = searcher.rewrite(booleanQuery);
            return searcher.createWeight(rewritten, ScoreMode.COMPLETE_NO_SCORES, 1f);
        }
        return null;
    }

    @Override
    public void visit(QueryVisitor visitor) {
        visitor.visitLeaf(this);
    }

    @Override
    public String toString(String field) {
        return field;
    }

    @Override
    public int hashCode() {
        return Objects.hash(
            field,
            Arrays.hashCode(queryVector),
            k,
            indexName,
            filterQuery,
            context,
            parentsFilter,
            radius,
            methodParameters,
            rescoreContext
        );
    }

    @Override
    public boolean equals(Object other) {
        return sameClassAs(other) && equalsTo(getClass().cast(other));
    }

    private boolean equalsTo(KNNQuery other) {
        if (other == this) return true;
        return Objects.equals(field, other.field)
            && Arrays.equals(queryVector, other.queryVector)
            && Arrays.equals(byteQueryVector, other.byteQueryVector)
            && Objects.equals(k, other.k)
            && Objects.equals(methodParameters, other.methodParameters)
            && Objects.equals(radius, other.radius)
            && Objects.equals(context, other.context)
            && Objects.equals(indexName, other.indexName)
            && Objects.equals(parentsFilter, other.parentsFilter)
            && Objects.equals(filterQuery, other.filterQuery)
            && Objects.equals(rescoreContext, other.rescoreContext);
    }

    /**
     * Context for KNNQuery
     */
    @Setter
    @Getter
    @AllArgsConstructor
    @EqualsAndHashCode
    public static class Context {
        int maxResultWindow;
    }
}
