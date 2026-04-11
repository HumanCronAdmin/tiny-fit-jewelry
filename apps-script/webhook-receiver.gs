/**
 * TinyFit Form Webhook Receiver v3
 * Super simple version — handles FORMLOVA's known payload format directly.
 */

const BRANDS_URL = 'https://raw.githubusercontent.com/HumanCronAdmin/tiny-fit-jewelry/master/data/brands.json';
const DATABASE_URL = 'https://humancronadmin.github.io/tiny-fit-jewelry/database.html';
const OWNER_EMAIL = 'korumono2929@gmail.com';
const SENDER_NAME = 'TinyFit Jewelry';

function doGet(e) {
  return jsonResponse({ ok: true, version: 'v3', ts: new Date().toISOString() });
}

function doPost(e) {
  var rawPayload = '';
  try {
    rawPayload = (e && e.postData) ? e.postData.contents : '{}';
    var payload = JSON.parse(rawPayload);
    var data = payload.data || {};

    var ringSize = data['69391'] || '';
    var wristSize = data['69392'] || '';
    var categoryRaw = data['69393'] || [];
    var style = data['69394'] || '';
    var frustration = data['69395'] || '';
    var email = data['69396'] || '';
    var newsletterOptIn = data['69397'] || '';

    if (!email) {
      throw new Error('No email in data. Keys: ' + Object.keys(data).join(','));
    }

    var category = Array.isArray(categoryRaw) ? categoryRaw : [categoryRaw];

    var brands = fetchBrands();
    var matched = pickBrands(brands, ringSize, wristSize, category);
    var emailContent = buildEmail(ringSize, matched);

    GmailApp.sendEmail(email, emailContent.subject, emailContent.body, { name: SENDER_NAME });

    var wantsNewsletter = isYes(newsletterOptIn);
    var subscribed = false;
    if (wantsNewsletter) {
      try {
        addSubscriber(email, ringSize, wristSize);
        subscribed = true;
      } catch (bdErr) {
        console.log('Buttondown add skipped: ' + bdErr.toString());
      }
    }

    return jsonResponse({ ok: true, matched: matched.length, email: email, subscribed: subscribed });
  } catch (err) {
    try {
      GmailApp.sendEmail(
        OWNER_EMAIL,
        '[TinyFit] Webhook error v3',
        'Error: ' + err.toString() + '\n\nRaw payload:\n' + rawPayload.substring(0, 4000),
        { name: 'TinyFit Webhook' }
      );
    } catch (_) {}
    return jsonResponse({ ok: false, error: err.toString() });
  }
}

function isYes(value) {
  if (value === true) return true;
  if (typeof value !== 'string') return false;
  var v = value.toLowerCase().trim();
  return v === 'yes' || v === 'true' || v === 'y' || v === '1' || v === 'はい';
}

function jsonResponse(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function fetchBrands() {
  var res = UrlFetchApp.fetch(BRANDS_URL, { muteHttpExceptions: true });
  if (res.getResponseCode() !== 200) {
    throw new Error('Failed to fetch brands.json: ' + res.getResponseCode());
  }
  return JSON.parse(res.getContentText());
}

function pickBrands(brands, ringSize, wristSize, category) {
  var ringMap = { 'under_3': 2, '3': 3, '3_5': 3.5, '4': 4, 'not_sure': 4 };
  var wristMap = { 'under_13': 13, '13_14': 14, '14_15': 15, 'bigger': 99 };
  var ringMax = (ringMap[ringSize] != null) ? ringMap[ringSize] : 4;
  var wristMax = (wristMap[wristSize] != null) ? wristMap[wristSize] : 15;

  var wantRings = category.indexOf('rings') !== -1;
  var wantBracelets = category.indexOf('bracelets') !== -1;

  var filtered = [];
  for (var i = 0; i < brands.length; i++) {
    var b = brands[i];
    if (!b.shop_url) continue;

    var minRing = (b.min_ring_size_us != null) ? b.min_ring_size_us : 99;
    var minWrist = (b.min_bracelet_cm != null) ? b.min_bracelet_cm : 99;
    var cats = b.category || [];

    var ok = false;
    if (wantRings && cats.indexOf('ring') !== -1 && minRing <= ringMax) ok = true;
    if (wantBracelets && cats.indexOf('bracelet') !== -1 && minWrist <= wristMax) ok = true;
    if (!wantRings && !wantBracelets && (minRing <= ringMax || minWrist <= wristMax)) ok = true;

    if (ok) filtered.push(b);
  }

  filtered.sort(function (a, b) { return scoreFit(b) - scoreFit(a); });
  return filtered.slice(0, 3);
}

function scoreFit(brand) {
  var fit = brand.fit_score;
  if (!fit || typeof fit !== 'object') return 0;
  var sum = 0;
  for (var k in fit) {
    if (typeof fit[k] === 'number') sum += fit[k];
  }
  return sum;
}

function buildEmail(ringSize, brands) {
  var sizeLabels = {
    'under_3': 'under size 3',
    '3': 'size 3',
    '3_5': 'size 3.5',
    '4': 'size 4',
    'not_sure': 'your size',
  };
  var sizeLabel = sizeLabels[ringSize] || 'your size';

  var subject = 'Your picks — brands that fit ' + sizeLabel;
  var body = 'Hey,\n\n';
  body += 'Chikako here from TinyFit Jewelry — thanks for taking the quiz.\n\n';

  if (brands.length === 0) {
    body += "I don't have enough brand matches for your exact combo yet.\n";
    body += 'Check the full database and I will send new picks as I find them:\n';
    body += '-> ' + DATABASE_URL + '\n\n';
  } else {
    body += 'Based on your answers, here are ' + brands.length + ' brands to start with:\n\n';
    for (var i = 0; i < brands.length; i++) {
      var b = brands[i];
      body += (i + 1) + '. ' + b.brand + '\n';
      if (b.petite_tip) {
        body += '   ' + String(b.petite_tip).trim() + '\n';
      }
      body += '   -> ' + b.shop_url + '\n\n';
    }
    body += 'Browse the full database:\n-> ' + DATABASE_URL + '\n\n';
  }

  body += "Found a brand that fits but isn't listed? Hit reply and tell me. Every tip goes in.\n\n";
  body += 'Talk soon,\nChikako\n';

  return { subject: subject, body: body };
}

function addSubscriber(email, ringSize, wristSize) {
  var apiKey = PropertiesService.getScriptProperties().getProperty('BUTTONDOWN_API_KEY');
  if (!apiKey) throw new Error('BUTTONDOWN_API_KEY not set');

  var payload = {
    email_address: email,
    type: 'regular',
    metadata: { ring_size: ringSize, wrist_size: wristSize },
  };

  var res = UrlFetchApp.fetch('https://api.buttondown.com/v1/subscribers', {
    method: 'post',
    contentType: 'application/json',
    headers: { 'Authorization': 'Token ' + apiKey },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });

  var code = res.getResponseCode();
  if (code >= 500) {
    throw new Error('Buttondown ' + code + ': ' + res.getContentText().substring(0, 200));
  }
  return res.getContentText();
}

function testExtractSelf() {
  var testPayload = {
    form_id: 33248,
    response_id: 1,
    data: {
      '69391': 'under_3',
      '69392': 'under_13',
      '69393': ['rings'],
      '69394': 'minimal',
      '69396': OWNER_EMAIL,
    },
  };
  var e = { postData: { contents: JSON.stringify(testPayload) } };
  var result = doPost(e);
  console.log(result.getContent());
}
