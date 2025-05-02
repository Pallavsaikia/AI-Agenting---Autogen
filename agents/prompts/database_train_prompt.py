from semantic_kernel.contents.chat_history import ChatHistory

class DatabaseTrainPrompt:
    def __init__(self,chat_history:ChatHistory,debug=False):
        self.chat_history=chat_history
        self.debug=debug
        self.chat_history.add_user_message("for the survey 'survey march' i want to see the highest scorer for all the scores  in all category")
        self.chat_history.add_assistant_message("""
```sql
SELECT
    u.fullname,
    oc.closeness_centrality,
    oc.betweenness_centrality,
    oc.local_clustering,
    oc.in_degree,
    oc.out_degree,
    oc.eigenvector,
    oc.page_rank,
    oc.hub_score,
    oc.authority_score,
    oc.reciprocity
FROM
    [opm_calculation] oc
JOIN
    [network_survey] ns ON oc.survey_id = ns.id
JOIN
    [teams] t ON ns.teamID = t.id
JOIN
    [user] u ON oc.user_id = u.id
JOIN
    [network_category] nc ON oc.category_id = nc.id
WHERE
    ns.name = 'network survey' AND
    nc.name = 'Innovation'
ORDER BY
    oc.closeness_centrality DESC,
    oc.betweenness_centrality DESC,
    oc.local_clustering DESC,
    oc.in_degree DESC,
    oc.out_degree DESC,
    oc.eigenvector DESC,
     oc.page_rank DESC,
     oc.hub_score DESC,
     oc.authority_score DESC,
     oc.reciprocity DESC;
```
                                                """)
        
        self.chat_history.add_user_message("Wrong.For query this complex i believe it should be separate queries")
        
        
        self.chat_history.add_assistant_message("""
```sql
-- Query for Highest Scorers by Closeness Centrality
SELECT TOP 1
    u.fullname AS fullname,
    nc.name AS category_name,
    oc.closeness_centrality AS Score
FROM
    [opm_calculation] oc
JOIN
    [user] u ON oc.user_id = u.id
JOIN
    [network_category] nc ON oc.category_id = nc.id
WHERE
    oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'survey march')
ORDER BY
    oc.closeness_centrality DESC;

-- Query for Highest Scorers by Betweenness Centrality
SELECT TOP 1
    u.fullname AS fullname,
    nc.name AS category_name,
    oc.betweenness_centrality AS Score
FROM
    [opm_calculation] oc
JOIN
    [user] u ON oc.user_id = u.id
JOIN
    [network_category] nc ON oc.category_id = nc.id
WHERE
    oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'survey march')
ORDER BY
    oc.betweenness_centrality DESC;

-- Query for Highest Scorers by Local Clustering
SELECT TOP 1
    u.fullname AS fullname,
    nc.name AS category_name,
    oc.local_clustering AS Score
FROM
    [opm_calculation] oc
JOIN
    [user] u ON oc.user_id = u.id
JOIN
    [network_category] nc ON oc.category_id = nc.id
WHERE
    oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'survey march')
ORDER BY
    oc.local_clustering DESC;
```
""")
        self.chat_history.add_user_message("no i want highest in each category")     
        self.chat_history.add_assistant_message("""
```sql
-- Query for Highest Scorers by Closeness Centrality in Each Category
SELECT
    u.fullname AS fullname,
    nc.name AS category_name,
    oc.closeness_centrality AS closeness_centrality_score
FROM
    [opm_calculation] oc
JOIN
    [user] u ON oc.user_id = u.id
JOIN
    [network_category] nc ON oc.category_id = nc.id
WHERE
    oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'survey march')
AND
    oc.closeness_centrality = (SELECT MAX(closeness_centrality) FROM [opm_calculation] WHERE survey_id = oc.survey_id AND category_id = oc.category_id)
ORDER BY
    nc.name;

-- Query for Highest Scorers by Betweenness Centrality in Each Category
SELECT
    u.fullname AS user_name,
    nc.name AS category_name,
    oc.betweenness_centrality AS betweenness_centrality_score
FROM
    [opm_calculation] oc
JOIN
    [user] u ON oc.user_id = u.id
JOIN
    [network_category] nc ON oc.category_id = nc.id
WHERE
    oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'survey march')
AND
    oc.betweenness_centrality = (SELECT MAX(betweenness_centrality) FROM [opm_calculation] WHERE survey_id = oc.survey_id AND category_id = oc.category_id)
ORDER BY
    nc.name;
```
                                                """)   
        
        self.chat_history.add_user_message("***Correct! now do it for all scores. and always include category name and user name for all relevant queries related  to score***")
        
        
        
#         self.chat_history.add_user_message("who are the highest scorers in different scores for the survey 'network survey' and category 'Innovation'")
#         self.chat_history.add_assistant_message("""
# ```sql
# SELECT
#     u.fullname,
#     oc.closeness_centrality
# FROM
#     [opm_calculation] oc
# JOIN
#     [user] u ON oc.user_id = u.id
# WHERE
#     oc.category_id IN (SELECT id FROM [network_category])
# GROUP BY
#     u.fullname, oc.closeness_centrality
# HAVING
#     oc.closeness_centrality = (SELECT MAX(closeness_centrality) FROM [opm_calculation] WHERE category_id = oc.category_id);

# -- Query for Highest Scorers by Betweenness Centrality
# SELECT
#     u.fullname,
#     oc.betweenness_centrality
# FROM
#     [opm_calculation] oc
# JOIN
#     [user] u ON oc.user_id = u.id
# WHERE
#     oc.category_id IN (SELECT id FROM [network_category])
# GROUP BY
#     u.fullname, oc.betweenness_centrality
# HAVING
#     oc.betweenness_centrality = (SELECT MAX(betweenness_centrality) FROM [opm_calculation] WHERE category_id = oc.category_id)
# ```
# """)
#         self.chat_history.add_user_message("""
#                                            Wrong!Following error,
#                                            Msg 8121, Level 16, State 1, Line 13
# Column 'opm_calculation.category_id' is invalid in the HAVING clause because it is not contained in either an aggregate function or the GROUP BY clause.
# Msg 8121, Level 16, State 1, Line 28
# Column 'opm_calculation.category_id' is invalid in the HAVING clause because it is not contained in either an aggregate function or the GROUP BY clause.
# Msg 8121, Level 16, State 1, Line 43""")
#         self.chat_history.add_assistant_message("""
# ```sql
# SELECT
#     u.fullname,
#     oc.closeness_centrality,
#     oc.betweenness_centrality,
#     oc.local_clustering,
#     oc.in_degree,
#     oc.out_degree,
#     oc.eigenvector,
#     oc.page_rank,
#     oc.hub_score,
#     oc.authority_score,
#     oc.reciprocity
# FROM
#     [opm_calculation] oc
# JOIN
#     [network_survey] ns ON oc.survey_id = ns.id
# JOIN
#     [teams] t ON ns.teamID = t.id
# JOIN
#     [user] u ON oc.user_id = u.id
# JOIN
#     [network_category] nc ON oc.category_id = nc.id
# WHERE
#     ns.name = 'network survey' AND
#     nc.name = 'Innovation'
# ORDER BY
#     oc.closeness_centrality DESC,
#     oc.betweenness_centrality DESC,
#     oc.local_clustering DESC,
#     oc.in_degree DESC,
#     oc.out_degree DESC,
#     oc.eigenvector DESC,
#     oc.page_rank DESC,
#     oc.hub_score DESC,
#     oc.authority_score DESC,
#     oc.reciprocity DESC;
# ```
#                                                 """)
    
#         self.chat_history.add_user_message("i think multiple separate queries required here.")
#         self.chat_history.add_assistant_message("""
# ```sql
# -- Query for Highest Scorers by Closeness Centrality
# SELECT TOP 1
#     u.fullname,
#     oc.closeness_centrality
# FROM
#     [opm_calculation] oc
# JOIN
#     [user] u ON oc.user_id = u.id
# WHERE
#     oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'network survey') AND
#     oc.category_id = (SELECT id FROM [network_category] WHERE name = 'Innovation')
# ORDER BY
#     oc.closeness_centrality DESC;

# -- Query for Highest Scorers by Betweenness Centrality
# SELECT TOP 1
#     u.fullname,
#     oc.betweenness_centrality
# FROM
#     [opm_calculation] oc
# JOIN
#     [user] u ON oc.user_id = u.id
# WHERE
#     oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'network survey') AND
#     oc.category_id = (SELECT id FROM [network_category] WHERE name = 'Innovation')
# ORDER BY
#     oc.betweenness_centrality DESC;

#                                                 """)
#         if not self.debug:
#             self.chat_history.add_user_message("Give me in proper json array structure")
#             self.chat_history.add_assistant_message("""
# {'response':
# [
# 'SELECT TOP 1 
# u.fullname,
# oc.closeness_centrality
# FROM
#     [opm_calculation] oc
# JOIN
#     [user] u ON oc.user_id = u.id
# WHERE
#     oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'network survey') AND
#     oc.category_id = (SELECT id FROM [network_category] WHERE name = 'Innovation')
# ORDER BY
#     oc.closeness_centrality DESC;',
    
# '
# SELECT TOP 1 
#     u.fullname,
#     oc.betweenness_centrality
# FROM
#     [opm_calculation] oc
# JOIN
#     [user] u ON oc.user_id = u.id
# WHERE
#     oc.survey_id = (SELECT id FROM [network_survey] WHERE name = 'network survey') AND
#     oc.category_id = (SELECT id FROM [network_category] WHERE name = 'Innovation')
# ORDER BY
#     oc.betweenness_centrality DESC;
# '
# ]}""")
#         self.chat_history.add_user_message("***Correct! now do it for all scores. and always include category name and user name for all relevant queries related  to score***")
    
#         self.chat_history.add_user_message("Now i ")