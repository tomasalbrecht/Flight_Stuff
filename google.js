

const API_KEY = '1234';
const options =  { write: __dirname + '/data'};
const qpx = require('google-flights-api')(API_KEY, options);

const q = {
   adultCount: 1, 
   maxPrice: 'EUR5000', 
   solutions: 1, 
   origin: 'DUB',
   destination: 'GDN', 
   date: '2016-12-14'
};
qpx.query(q).then((data) => {
  //data looks like: [ { airline: 'SK', price: 'EUR71.10' } ]
}).catch(console.error);