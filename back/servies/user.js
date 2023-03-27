const db = require('./db');
const helper = require('../helper');
const config = require('../config');

async function getUserByEmail(body){
  console.log(body.kakao_account);
  const rows = await db.query(
      `select count(*) as vaild from users where user_email = "${body.kakao_account.email}"`
  );
  const data = helper.emptyOrRows(rows);
  console.log(rows);
  return {
    data
  }
}
async function getUserByEmail2(body){
  console.log(body.kakao_account);
  const rows = await db.query(
      `select * from users where user_email = "${body.kakao_account.email}"`
  );
  const data = helper.emptyOrRows(rows);
  console.log(rows);
  return {
    data
  }
}

async function signUpUser(body){
  console.log(body.kakao_account);
  const rows = await db.query(
      `INSERT INTO users(user_email,user_name) values("${body.kakao_account.email}","${body.properties.nickname}")`
  );
  const data = helper.emptyOrRows(rows);
  console.log(rows);
  return {
    data
  }
}

module.exports = {
    getUserByEmail,
    signUpUser,
    getUserByEmail2
  }