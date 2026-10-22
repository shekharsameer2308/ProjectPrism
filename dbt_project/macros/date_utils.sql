{% macro timestamp_diff_seconds(end_timestamp, start_timestamp) %}
  {% if target.type == 'bigquery' %}
    timestamp_diff({{ end_timestamp }}, {{ start_timestamp }}, SECOND)
  {% else %}
    datediff('second', {{ start_timestamp }}, {{ end_timestamp }})
  {% endif %}
{% endmacro %}

{% macro date_diff_days(end_date, start_date) %}
  {% if target.type == 'bigquery' %}
    date_diff({{ end_date }}, {{ start_date }}, DAY)
  {% else %}
    datediff('day', {{ start_date }}, {{ end_date }})
  {% endif %}
{% endmacro %}
