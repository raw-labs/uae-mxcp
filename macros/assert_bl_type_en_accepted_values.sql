{% macro test_assert_bl_type_en_accepted_values(model, column_name) %}
    
    WITH validation_errors AS (
        SELECT
            {{ column_name }}
        FROM {{ model }}
        WHERE {{ column_name }} NOT IN (
            'Agrecultural & Animals',
            'Business Invest License',
            'Commercial',
            'E''dmad  (Reliance)',
            'E-Commerce License',
            'Educational License',
            'Event   License',
            'Handicraft',
            'Industrial',
            'International Business Companies',
            'Media License',
            'Preliminary License',
            'Professional',
            'Service',
            'Service License',
            'Standard',
            'Trade',
            'tourism license'
        )
    )

    SELECT *
    FROM validation_errors

{% endmacro %} 