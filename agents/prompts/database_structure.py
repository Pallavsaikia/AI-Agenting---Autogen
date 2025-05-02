TABLE_STRUCTURE_SYSTEM_PROMPT="""
Below are list of tables in DB and along with column name, description ,data_type and relationship.
📌 Tables, Columns, Data Types, and Descriptions:

1. teams (Description:stores all the teams.Teams are used to send survey to a group of data)
- name: nvarchar(255), NULL — name of the team.
- active: bit, NOT NULL — Indicates whether the team is active.
- dataverse_id: nvarchar(255), NULL — Unique identifier for the team in Dataverse.
- created_at: datetime, NULL — Timestamp when the team was created.
- modified_at: datetime, NULL — Timestamp when the team was last modified.

2. user (Description:stores all the user details in the system)
- id: int, NOT NULL, Primary Key — Unique identifier for the user.
- firstname: nvarchar(255), NOT NULL — User's first name.
- lastname: nvarchar(255), NULL — User's last name.
- fullname: nvarchar(255), NOT NULL — User's full name.
- username: nvarchar(255), NULL — User's username (unique identifier).
- email: nvarchar(255), NOT NULL — User's email address.
- company_id: int, NULL, Foreign Key → company.id — Company associated with the user.
- phoneno: nvarchar(50), NULL — User's phone number.
- inactive: bit, NULL — Indicates whether the user is inactive.
- dataverse_id: nvarchar(255), NULL — Dataverse unique identifier for the user.
- created_at: datetime, NULL — Timestamp when the user was created.
- modified_at: datetime, NULL — Timestamp when the user was last modified.

3. user_meta_field(Description:stores all the meta key against which a user might have a value e.g., "gender,department,worklevel,department" )
- id: int, NOT NULL, Primary Key — Unique identifier for the user meta field.
- name: nvarchar(255), NOT NULL — Name of the meta field (e.g., "gender,department,worklevel,department").
- isDefault: bit, NULL — Indicates whether the field is default.
- mysql_id: nvarchar(255), NULL — MySQL ID of the meta field.
- dataverse_id: nvarchar(255), NULL — Dataverse unique identifier for the meta field.
- created_at: datetime, NULL — Timestamp when the meta field was created.
- modified_at: datetime, NULL — Timestamp when the meta field was last modified.

4. user_meta_value(Description:stores all users meta key value against a team. Example for team x user A has user_meta_value of Male against user_meta_field of Gender")
- id: int, NOT NULL, Primary Key — Unique identifier for the user meta value.
- value: nvarchar(-1), NULL — The value stored in the meta field.
- dataverse_id: nvarchar(255), NULL — Dataverse unique identifier for the meta value.
- mysql_id: nvarchar(255), NULL — MySQL ID of the meta value.
- user_meta_field_id: int, NOT NULL, Foreign Key → user_meta_field.id — The meta field associated with this value.
- user_id: int, NOT NULL, Foreign Key → user.id — The user this meta value is associated with.
- team_id: int, NULL, Foreign Key → teams.id — The team this meta value is associated with.
- created_at: datetime, NULL — Timestamp when the meta value was created.
- modified_at: datetime, NULL — Timestamp when the meta value was last modified.

5. user_role
- id: int, NOT NULL, Primary Key — Unique identifier for the user role.
- user_id: int, NOT NULL, Foreign Key → user.id — User associated with this role.
- role_id: int, NOT NULL, Foreign Key → role.id — Role assigned to the user.
- created_at: datetime, NULL — Timestamp when the role was assigned to the user.
- updated_at: datetime, NULL — Timestamp when the role assignment was last updated.

6. company(Description:stores all company details" )
- name : nvarchar(255), NULL - Name of the company
- company_function_id: int, NULL, Foreign Key → company_function.id — The company function associated with this company.
- company_hierarchy_template_id: int, NULL, Foreign Key → company_hierarchy_template.id — The hierarchy template for the company.
- country_id: int, NULL, Foreign Key → country.id — The country associated with this company.
- division_id: int, NULL, Foreign Key → division.id — The division this company belongs to.
- group_id: int, NULL, Foreign Key → group.id — The group associated with this company.
- parent_hierarchy_structure_id: int, NULL, Foreign Key → company_hierarchy_structure.id — Parent hierarchy structure in the company hierarchy.
- region_id: int, NULL, Foreign Key → region.id — The region this company operates in.
- sbu_id: int, NULL, Foreign Key → sbu.id — The Strategic Business Unit (SBU) of this company.
- sector_id: int, NULL, Foreign Key → sector.id — The sector this company belongs to.

7. company_hierarchy_template
- hierarchy_template_id: int, NOT NULL, Primary Key — Unique identifier for the company hierarchy template.
- hierarchy_type_id: int, NULL, Foreign Key → hierarchy_type.id — Type of hierarchy for the template.
- created_by: int, NULL, Foreign Key → user.id — The user who created the hierarchy template.
- modified_by: int, NULL, Foreign Key → user.id — The user who last modified the hierarchy template.

8. company_hierarchy_structure
- parent_hierarchy_structure_id: int, NULL, Foreign Key → company_hierarchy_structure.id — Parent hierarchy structure.
- hierarchy_template_id: int, NULL, Foreign Key → company_hierarchy_template.id — Hierarchy template ID used for this structure.
- hierarchy_type_id: int, NULL, Foreign Key → hierarchy_type.id — Type of hierarchy.
- created_by: int, NULL, Foreign Key → user.id — The user who created the hierarchy structure.
- modified_by: int, NULL, Foreign Key → user.id — The user who last modified the hierarchy structure.

9. hierarchy_template_backbone
- company_hierarchy_template_id: int, NOT NULL, Foreign Key → company_hierarchy_template.id — The associated hierarchy template for the backbone.
- created_by: int, NULL, Foreign Key → user.id — The user who created the backbone.
- modified_by: int, NULL, Foreign Key → user.id — The user who last modified the backbone.

10. company_practitioner
- company_id: int, NULL, Foreign Key → company.id — Company associated with the practitioner.
- created_by: int, NULL, Foreign Key → user.id — User who created the record.
- modified_by: int, NULL, Foreign Key → user.id — User who last modified the record.
- practitioner_id: int, NULL, Foreign Key → practitioner.id — Practitioner associated with the company.
- user_id: int, NULL, Foreign Key → user.id — User associated with the practitioner.

11. consultancy_practitioner
- consultancy_id: int, NULL, Foreign Key → consultancy.id — The consultancy the practitioner is associated with.
- practitioner_id: int, NULL, Foreign Key → practitioner.id — The practitioner in the consultancy.
- created_by: int, NULL, Foreign Key → user.id — User who created the record.
- modified_by: int, NULL, Foreign Key → user.id — User who last modified the record.

12. opm_calculation(Description:stores all survey calculated data")
- category_id: int, NULL, Foreign Key → network_category.id — Category of the operation measurement (OPM).
- survey_id: int, NULL, Foreign Key → network_survey.id — Survey related to the OPM calculation.
- user_id: int, NULL, Foreign Key → user.id — The user who performed the OPM calculation.
- closeness_centrality - stores the score of closeness_centrality
- betweenness_centrality: float, - stores the score of betweenness_centrality 
- local_clustering: float, - stores the score of local_clustering 
- in_degree: float, - stores the score of in_degree 
- out_degree: float, - stores the score of out_degree 
- eigenvector: float, - stores the score of eigenvector 
- page_rank: float, - stores the score of page_rank 
- hub_score: float, - stores the score of hub_score 
- authority_score: float, - stores the score of authority_score 
- reciprocity: float, - stores the score of reciprocity
 
13. network_category(Description:stores all categories available for creating a survey.Each category is in a group")
- name : nvarchar(255), NULL - Name of the category
- base_network_category_id: int, NULL, Foreign Key → network_category.id — Base category for the network category.
- network_group_id: int, NULL, Foreign Key → network_group.id — The group associated with the network category.
- network_template_id: int, NULL, Foreign Key → network_template.id — Template used for the network category.

14. network_group(Description:stores all groups available for creating a survey")
-name : nvarchar(255), NULL - Name of the group
- network_template_id: int, NULL, Foreign Key → network_template.id — The network template associated with the group.

15. network_survey_category
- network_category_id: int, NULL, Foreign Key → network_category.id — The network category associated with the survey.
- network_survey_id: int, NULL, Foreign Key → network_survey.id — The survey that contains the network category.

16. network_survey(Description:stores all surveys details like which template is used")
- name:nvarchar(255)NULL - Name of the survey
- company_id: int, NULL, Foreign Key → company.id — Company associated with the survey.
- network_template_id: int, NULL, Foreign Key → network_template.id — Template associated with the network survey.
- teamID: int, NULL, Foreign Key → teams.id — Team associated with the network survey.

17. network_survey_nominations(Description:stores all records of which nominator and nominee and order against category and survey")
- network_category_id: int, NULL, Foreign Key → network_category.id — The category for the nomination.
- network_survey_id: int, NULL, Foreign Key → network_survey.id — The network survey associated with the nominations.
- nominator_id: int, NULL, Foreign Key → user.id — User nominating another.
- nominee_id: int, NULL, Foreign Key → user.id — User being nominated.
- network_question_id: int, NULL, Foreign Key → network_question.id — The question related to the nomination.
- network_survey_questionnaire_id: int, NULL, Foreign Key → network_survey_questionnaire.id — Questionnaire related to the nomination.

18. network_survey_questionnaire (Description:This stores the questionnaire details of users in each survey")
- network_survey_id: int, NULL, Foreign Key → network_survey.id — Survey related to the questionnaire.
- user_id: int, NULL, Foreign Key → user.id — User filling out the questionnaire.
- status: nvarchar - Status of the questionnaire

19. network_template (Description:This is a list  template which is a superset which can include network question, category,group etc in it")
- company_id: int, NULL, Foreign Key → company.id — Company related to the template.

20. network_question (Description:This stores the question details")
- category_id: int, NULL, Foreign Key → network_category.id — Category for the network question.
- network_template_id: int, NULL, Foreign Key → network_template.id — Template related to the network question.
- header: nvarchar- header of the question
21. sbu
- groupid: int, NULL, Foreign Key → group.id — Group associated with the SBU.
- sector_id: int, NULL, Foreign Key → sector.id — Sector associated with the SBU.

***
For anything related to scores.This is the sequence to write query
1.opm_calculation->(survey,user,category)
2.suvey->teams->
3.user+teams->user_meta_field,user_meta_value
***
"""