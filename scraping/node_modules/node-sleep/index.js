var sleep = require('./build/Release/sleep.node');

exports.sleep = function(ms){
  console.log('nodejs will call native moudle to sleep ' + ms + ' ms');
  sleep.usleep(1000 * ms);
  return;
}


exports.usleep = function(us){
  console.log('nodejs will call native moudle to sleep ' + us + ' us');
  sleep.usleep(us);
  return;
}
