cube(`Customers`, {
  sql: `SELECT * FROM marts.dim_customers`,

  measures: {
    count: { type: `count`, title: `Customers` },
    repeat_customers: {
      type: `count`,
      filters: [{ sql: `${CUBE}.is_repeat_customer = TRUE` }],
      title: `Repeat Customers`,
    },
  },

  dimensions: {
    customer_id: { sql: `customer_id`, type: `string`, primaryKey: true },
    segment: { sql: `segment`, type: `string` },
    first_seen_date: { sql: `first_seen_date`, type: `time` },
  },
});
