function preproc(key,iv) {
    var ukey = CryptoJS.enc.Utf8.parse(key);
    var options = { iv: CryptoJS.enc.Utf8.parse(iv), mode:CryptoJS.mode.CFB, padding:CryptoJS.pad.ZeroPadding};
    var obj = {
        ukey: ukey,
        options: options
    }
    return obj;
}

function encrypt(plain_text,key,iv) {
    var attr = preproc(key,iv);
    var encrypted = CryptoJS.AES.encrypt(plain_text, attr.ukey, attr.options);
    var e64 = CryptoJS.enc.Base64.parse(encrypted.toString());
    var encrypted = e64.toString(CryptoJS.enc.Hex);
    return encrypted;
}

function decrypt(encrypted_text,key,iv) {
    var attr = preproc(key,iv);
    var reb64 = CryptoJS.enc.Hex.parse(encrypted_text);
    var bytes = reb64.toString(CryptoJS.enc.Base64);
    var decrypted = CryptoJS.AES.decrypt(bytes, attr.ukey, attr.options);
    return decrypted.toString(CryptoJS.enc.Utf8);
}
