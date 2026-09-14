cube(`Orders`, {
  sql: `SELECT * FROM marts.fct_orders`,

  measures: {
    count: { type: `count`, title: `Orders` },
    revenue: { sql: `revenue_usd`, type: `sum`, title: `Order Revenue` },
  },

  dimensions: {
    order_id: { sql: `order_id`, type: `string`, primaryKey: true },
    customer_id: { sql: `customer_id`, type: `string` },
    status: { sql: `status`, type: `string` },
    segment: { sql: `segment`, type: `string` },
    order_date: { sql: `order_date`, type: `time` },
  },
});
