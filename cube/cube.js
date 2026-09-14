module.exports = {
  dbType: process.env.CUBEJS_DB_TYPE || 'postgres',
  apiSecret: process.env.CUBEJS_API_SECRET,
  schemaPath: 'schema',
};
