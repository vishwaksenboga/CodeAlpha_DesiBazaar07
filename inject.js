const fs = require('fs');
let html = fs.readFileSync('DesiBazaar.html', 'utf8');

const vars = `
let cart = JSON.parse(localStorage.getItem('db_cart') || '[]');
let wishlist = JSON.parse(localStorage.getItem('db_wishlist') || '[]');
let orders = JSON.parse(localStorage.getItem('db_orders') || '[]');
const STATES = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'];
const CAT_ICON = {
  'Traditional Foods': 'bi-basket',
  'Regional Snacks': 'bi-cup-hot',
  'Tea & Coffee': 'bi-cup',
  'Organic Products': 'bi-leaf',
  'Home Decor': 'bi-house-heart',
  'Festival Specials': 'bi-stars',
  'Textiles': 'bi-layers',
  'Dry Fruits': 'bi-apple',
  'Handicrafts': 'bi-palette',
  'Beauty Products': 'bi-flower1',
  'Wellness Products': 'bi-heart-pulse',
  'Kitchen Essentials': 'bi-tools',
  'Eco-Friendly Products': 'bi-recycle',
  'Stationery': 'bi-journal-text',
  'Fashion Accessories': 'bi-handbag',
  'Spiritual Products': 'bi-yin-yang',
  'Toys': 'bi-controller',
  'Ayurvedic Products': 'bi-bandaid'
};
`;

if (!html.includes('let cart = JSON.parse')) {
  html = html.replace(/<script[^>]*>/, match => match + vars);
  fs.writeFileSync('DesiBazaar.html', html);
  console.log('Injected variables.');
} else {
  console.log('Variables already injected.');
}
