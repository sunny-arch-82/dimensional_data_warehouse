cube(`Metrics`, {
  sql: `SELECT * FROM marts.metric_snapshot`,

  measures: {
    gross_revenue: {
      sql: `gross_revenue`,
      type: `max`,
      title: `Gross Revenue`,
    },
    net_revenue: {
      sql: `net_revenue`,
      type: `max`,
      title: `Net Revenue`,
    },
    active_customers: {
      sql: `active_customers`,
      type: `max`,
      title: `Active Customers`,
    },
    average_order_value: {
      sql: `average_order_value`,
      type: `max`,
      title: `Average Order Value`,
    },
    refund_rate: {
      sql: `refund_rate`,
      type: `max`,
      title: `Refund Rate`,
    },
  },

  dimensions: {
    metric_as_of_date: {
      sql: `metric_as_of_date`,
      type: `time`,
      title: `Metric As Of Date`,
    },
  },
});
