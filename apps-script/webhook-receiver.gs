/**
 * TinyFit Form Webhook Receiver v3
 * Super simple version - handles FORMLOVA's known payload format directly.
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
  return v === 'yes' || v === 'true' || v === 'y' || v === '1';
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

  var catMap = {
    'rings': 'ring',
    'bracelets': 'bracelet',
    'necklaces': 'necklace',
    'anklets': 'anklet',
  };

  var wantedCats = [];
  for (var c = 0; c < category.length; c++) {
    var mapped = catMap[category[c]];
    if (mapped && wantedCats.indexOf(mapped) === -1) wantedCats.push(mapped);
  }
  if (wantedCats.length === 0) {
    wantedCats = ['ring', 'bracelet', 'necklace', 'anklet'];
  }

  var filtered = [];
  for (var i = 0; i < brands.length; i++) {
    var b = brands[i];
    if (!b.shop_url) continue;

    var minRing = (b.min_ring_size_us != null) ? b.min_ring_size_us : 99;
    var minWrist = (b.min_bracelet_cm != null) ? b.min_bracelet_cm : 99;
    var cats = b.category || [];

    var matched = false;
    for (var w = 0; w < wantedCats.length; w++) {
      var wantedCat = wantedCats[w];
      if (cats.indexOf(wantedCat) === -1) continue;

      if (wantedCat === 'ring') {
        if (minRing <= ringMax) { matched = true; break; }
      } else if (wantedCat === 'bracelet') {
        if (minWrist <= wristMax) { matched = true; break; }
      } else {
        matched = true;
        break;
      }
    }

    if (matched) filtered.push(b);
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

  var subject = 'Your picks - brands that fit ' + sizeLabel;
  var body = 'Hey,\n\n';
  body += 'Chikako here from TinyFit Jewelry - thanks for taking the quiz.\n\n';

  if (brands.length === 0) {
    body += "I'm sorry - I don't have a brand in my database that matches your combo yet.\n\n";
    body += "This is why TinyFit exists. Jewelry for ring size 2, 3, 4 - or wrists under 14cm - is hard to find. Most brands don't make it. I add new brands to the database as I find them.\n\n";
    body += "Browse the full database here:\n-> " + DATABASE_URL + "\n\n";
  } else if (brands.length === 3) {
    body += "Here are 3 brands that fit your combo:\n\n";
    for (var i = 0; i < brands.length; i++) {
      var b = brands[i];
      body += (i + 1) + '. ' + b.brand + '\n';
      if (b.petite_tip) {
        body += '   ' + String(b.petite_tip).trim() + '\n';
      }
      body += '   -> ' + b.shop_url + '\n\n';
    }
    body += 'Browse the full database:\n-> ' + DATABASE_URL + '\n\n';
  } else {
    var oneMatch = brands.length === 1;
    body += "Sorry - I've only got " + (oneMatch ? '1 brand' : brands.length + ' brands') + " that " + (oneMatch ? 'fits' : 'fit') + " your combo right now.\n\n";
    for (var j = 0; j < brands.length; j++) {
      var bb = brands[j];
      body += (j + 1) + '. ' + bb.brand + '\n';
      if (bb.petite_tip) {
        body += '   ' + String(bb.petite_tip).trim() + '\n';
      }
      body += '   -> ' + bb.shop_url + '\n\n';
    }
    body += "The database is still growing - I add new brands whenever I find a new one that fits.\n\n";
    body += 'Browse the full database:\n-> ' + DATABASE_URL + '\n\n';
  }

  body += "Found a brand that fits but isn't listed? Hit reply and tell me. Every tip goes in.\n\n";
  body += 'Talk soon,\nChikako\n';

  return { subject: subject, body: body };
}

function addSubscriber(email, ringSize, wristSize) {
  var apiKey = PropertiesService.getScriptProperties().getProperty('BUTTONDOWN_API_KEY');
  if (!apiKey) throw new Error('BUTTONDOWN_API_KEY not set');

  var metadata = { ring_size: ringSize, wrist_size: wristSize };
  var headers = { 'Authorization': 'Token ' + apiKey };

  var createRes = UrlFetchApp.fetch('https://api.buttondown.com/v1/subscribers', {
    method: 'post',
    contentType: 'application/json',
    headers: headers,
    payload: JSON.stringify({
      email_address: email,
      type: 'regular',
      metadata: metadata,
    }),
    muteHttpExceptions: true,
  });
  var createCode = createRes.getResponseCode();

  if (createCode === 200 || createCode === 201) {
    return createRes.getContentText();
  }

  var patchRes = UrlFetchApp.fetch('https://api.buttondown.com/v1/subscribers/' + encodeURIComponent(email), {
    method: 'patch',
    contentType: 'application/json',
    headers: headers,
    payload: JSON.stringify({ metadata: metadata }),
    muteHttpExceptions: true,
  });
  var patchCode = patchRes.getResponseCode();

  if (patchCode >= 200 && patchCode < 300) {
    return 'updated: ' + patchRes.getContentText();
  }

  throw new Error('Buttondown create=' + createCode + ' patch=' + patchCode + ': ' + patchRes.getContentText().substring(0, 200));
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
