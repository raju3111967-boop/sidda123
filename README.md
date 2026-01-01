# सिध्द गौतम को-ऑप हौसिंग सोसायटी वेबसाईट

## प्रोजेक्ट माहिती

**सोसायटीचे नाव:** सिध्द गौतम को-ऑप हौसिंग सोसायटी लि.  
**पत्ता:** 429/1अ मानेकशा नगर, द्वारका, नाशिक शहर – 422011  
**रजिस्ट्रेशन नं:** NSK/HSG(T.C)/507/1987  
**Developer:** श्री. राजेश भालेराव | Mob: 9552840443

## तंत्रज्ञान

- **Backend:** Python Flask
- **Database:** SQLite (MySQL ready)
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication:** Session-based
- **Language:** मराठी (Marathi Unicode)

## वैशिष्ट्ये

### सदस्य (Member) Features:
- ✅ नोंदणी आणि लॉगिन
- ✅ डॅशबोर्ड
- ✅ सूचना फलक
- ✅ तक्रार व्यवस्थापन
- ✅ रिडेव्हलपमेंट प्रगती
- ✅ दस्तऐवज डाउनलोड
- ✅ प्रोफाईल व्यवस्थापन
- ✅ पासवर्ड रीसेट

### अॅडमिन (Admin) Features:
- ✅ सदस्य व्यवस्थापन
- ✅ संचालक मंडळ व्यवस्थापन
- ✅ सूचना प्रकाशन
- ✅ तक्रारींना उत्तर
- ✅ रिडेव्हलपमेंट अपडेट्स
- ✅ लॉगिन इतिहास
- ✅ डॅशबोर्ड आकडेवारी

## इन्स्टॉलेशन

### 1. Virtual Environment तयार करा
```bash
python -m venv venv
```

### 2. Virtual Environment Activate करा

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Dependencies Install करा
```bash
pip install -r requirements.txt
```

### 4. Application चालवा
```bash
python app.py
```

### 5. Browser मध्ये उघडा
```
http://localhost:5000
```

## डिफॉल्ट लॉगिन

**Admin:**
- Username: `admin`
- Password: `123`

## प्रोजेक्ट स्ट्रक्चर

```
sidda/
├── app.py                      # मुख्य Flask ऍप्लिकेशन
├── requirements.txt            # Python dependencies
├── society.db                  # SQLite डेटाबेस (auto-created)
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # मुख्य CSS
│   │   ├── js/
│   │   │   └── main.js        # मुख्य JavaScript
│   │   ├── images/            # Images फोल्डर
│   │   └── uploads/           # Uploaded files
│   └── templates/
│       ├── base.html          # बेस टेम्पलेट
│       ├── index.html         # मुख्य पृष्ठ
│       ├── auth/
│       │   ├── login.html     # लॉगिन पृष्ठ
│       │   └── register.html  # नोंदणी पृष्ठ
│       ├── member/
│       │   ├── dashboard.html
│       │   ├── profile.html
│       │   ├── complaints.html
│       │   ├── notices.html
│       │   ├── redevelopment.html
│       │   └── documents.html
│       └── admin/
│           ├── dashboard.html
│           ├── members.html
│           ├── directors.html
│           ├── notices.html
│           ├── complaints.html
│           └── redevelopment.html
```

## डेटाबेस मॉडेल्स

1. **Member** - सदस्य माहिती
2. **Director** - संचालक मंडळ
3. **Notice** - सूचना
4. **Complaint** - तक्रारी
5. **Document** - दस्तऐवज
6. **RedevelopmentUpdate** - रिडेव्हलपमेंट अपडेट्स
7. **LoginHistory** - लॉगिन इतिहास

## महत्वाचे नोट्स

- डेटा कधीही डिलीट होणार नाही (Persistent Storage)
- सर्व पासवर्ड्स hashed स्वरूपात जतन होतात
- Mobile-first responsive design
- Bootstrap 5 वापरून तयार
- Marathi Unicode support
- Future-ready for MySQL migration

## संचालक मंडळ (Pre-loaded)

1. श्री. शामराव बाबुराव मोरे – चेअरमन – 9423557744
2. श्री दिपक भगवानदास मोरे – सचिव – 9922030401
3. श्री. श्रीकांत विठ्ठल शेरे – खजिनदार – 8237626246
4. श्री. जिवन बाबुराव वाघ – सदस्य – 9763439323
5. श्री. त्रंबक सोनु सांगळे – सदस्य – 8237626246
6. श्री. अमोल मधुकर म्हेमाने – सदस्य – 9890322301
7. श्री. रुपेश शरद पहाडी – सदस्य – 9921310205
8. श्री. देविदास तुळशीराम सुर्यवंशी – सदस्य – 9225117519
9. श्री. सुभाष सोपन भवर – सदस्य – 901105974
10. सौ. कविता अनिल अंभगे – सदस्य – 9823776948
11. श्रीमती माधुरी अशोक गांगुर्डे – सदस्य – 9270619888

## भविष्यातील सुधारणा

- [ ] AI-powered complaint classification
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Payment gateway integration
- [ ] Mobile app
- [ ] Document upload functionality
- [ ] Advanced reporting
- [ ] Multi-language support

## Support

**Developer:** श्री. राजेश भालेराव  
**Mobile:** 9552840443  
**Email:** (Add your email)

---

© 2025 सिध्द गौतम को-ऑप हौसिंग सोसायटी लि. सर्व हक्क राखीव.
