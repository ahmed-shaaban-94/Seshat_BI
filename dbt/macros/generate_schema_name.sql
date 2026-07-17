{% macro generate_schema_name(custom_schema_name, node) -%}
  {%- set allowed_schemas = ['silver', 'gold', 'audit'] -%}
  {%- if custom_schema_name is none -%}
    {{ exceptions.raise_compiler_error(
      'Every governed model must declare a shadow layer.'
    ) }}
  {%- endif -%}
  {%- set requested_schema = custom_schema_name | trim | lower -%}
  {%- set governed_test_schema = (
    node.resource_type == 'test'
    and requested_schema == 'dbt_test__audit'
  ) -%}
  {%- if requested_schema not in allowed_schemas and not governed_test_schema -%}
    {{ exceptions.raise_compiler_error(
      'Unsupported governed model layer: ' ~ requested_schema
    ) }}
  {%- endif -%}
  {{ target.schema }}_{{ requested_schema }}
{%- endmacro %}
