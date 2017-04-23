var express = require('express');
var url = require('url');
var router = express.Router();



/* GET users listing. */
router.get('/', function(req, res, next) {
	var queryData = url.parse(req.url, true).query;
  res.io.emit("socketToMe", [queryData.name, queryData.tablica, queryData.alert]);
  res.send('respond with a resource.');
});

module.exports = router;
