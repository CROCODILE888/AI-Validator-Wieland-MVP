"""
Schema definitions for Databricks tables - used as LLM context.
"""

SCHEMA_CONTEXT = """
You are working with Databricks SQL tables in the workspace.default schema.

Table: workspace.default.wieland_routing_ca03
Description: SAP routing operations data. Each row is one manufacturing operation step.
Key columns:
- Object_ID_PLPO_ARBID: workstation/machine ID (string)
- Activity_PLPO_VORNR: operation number
- Number_of_employees_PLPO_ANZMA: number of workers assigned in SAP
- Operation_short_text_PLPO_LTXA1: operation description
- Plant_PLPO_WERKS: plant code
- Group_PLPO_PLNNR: routing group number
- Task_List_Type_PLPO_PLNTY: task list type

Table: workspace.default.machine_master
Description: Master reference data for machines/workstations. Source of truth for correct number of workers per machine.
Key columns:
- machine_id: workstation ID (matches Object_ID_PLPO_ARBID)
- workshop: workshop name
- number_workers: correct/expected number of workers

Table: workspace.default.wieland_bom_cs03
Description: SAP Bill of Materials data.
Key columns:
- Material_MAST_MATNR: material number
- Plant_MAST_WERKS: plant
- Component_STPO_IDNRK: component material number
- Component_Quantity_STPO_MENGE: component quantity
- Component_UoM_STPO_MEINS: unit of measure
- Item_category_STPO_POSTP: item category
"""
