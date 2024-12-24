function valid_string(name){
    const allowed_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
    for(var i=0;i<name.length;i++){
        if(allowed_chars.indexOf(name[i]) == -1){
            return false;
        }
    }
    return true;
}

function valid_password(){
    const password = document.getElementById("password").value;
    if (password.length < 8) {
        alert("Password must be at least 8 characters long.");
        return false;
    }
    var upper = false;
    var lower = false;
    var special = false;
    var digit = false;
    var special_chars = '~!@#$%^&*_'
    var digits = '0123456789'

    for(var i=0;i<password.length;i++){
        if(password[i] >= 'A' && password[i] <= 'Z'){
            upper = true;
        }
        if(password[i] >= 'a' && password[i] <= 'z'){
            lower = true;
        }
        if(special_chars.indexOf(password[i]) != -1){
            special = true;
        }
        if(digits.indexOf(password[i]) != -1){
            digit = true;
        }
    }

    if(!upper){
        alert("Password must contain an upper case letter.");
        return false;
    }
    if(!lower){
        alert("Password must contain a lower case letter.");
        return false;
    }
    if(!special){
        alert("Password must contain a special character.");
        return false;
    }
    if(!digit){
        alert("Password must contain a digit(0-9).");
        return false;
    }
    return true;
}

function confirm_password(){
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirm_password").value;
    if(password!=confirm){
        alert("Password and Confirmation Password don't match. Re-enter.");
        return false;
    }
    return true;
}

function valid_pincode(){
    const pincode = document.getElementById("pincode").value;
    if(pincode.length != 6){
        alert("Incorrect pincode. Should be of 6 digits.")
        return false;
    }
    return true;
}

function valid_phone(){
    const phone = document.getElementById("phone_no").value;
    if(phone.length != 10){
        alert("Incorrect phone number. Should be of 10 digits.")
        return false;
    }
    return true;
}

function signup_validation() {
    flag = true;
    const name = document.getElementById("name").value;
    const city = document.getElementById("city").value;
    if(!valid_string(name)){
        alert("Invalid name. Should only include characters and spaces");
        flag = false;
    }
    if(!valid_string(city)){
        alert("Invalid city. Should only include characters and spaces");
        flag = false;
    }
    if(!valid_password()){
        flag = false;
    }
    if(!confirm_password()){
        flag = false;
    }
    if(!valid_pincode()){
        flag = false;
    }
    if(!valid_phone()){
        flag = false;
    }
    return flag;
}

function update_validation(){
    flag = true;
    const name = document.getElementById("name").value;
    const city = document.getElementById("city").value;
    if(!valid_string(name)){
        alert("Invalid name. Should only include characters and spaces");
        flag = false;
    }
    if(!valid_string(city)){
        alert("Invalid city. Should only include characters and spaces");
        flag = false;
    }
    if(!valid_pincode()){
        flag = false;
    }
    if(!valid_phone()){
        flag = false;
    }
    return flag;
}

function open_popup(id){
    document.getElementById(id).style.display = "block";

}
function close_popup(id){
    document.getElementById(id).style.display = "none";
}

function add_service(button){
    const row = button.closest('tr')
    const service_id = row.getAttribute('service_id');
    document.getElementById('service_id').value = service_id;
    document.getElementById('add_service').style.display = "none";
}

function book_service(button){
    open_popup('add_service');
    const row = button.closest('tr')
    const service_id = row.getAttribute('service_id');
    document.getElementById('service_id').value = service_id;
}

function edit_request(button){
    open_popup('add_service');
    const row = button.closest('tr')
    const request_id = row.getAttribute('request_id');
    document.getElementById('request_id').value = request_id;
}

function complete_request(button){
    open_popup('complete_request');
    const row = button.closest('tr')
    const request_id = row.getAttribute('request_id');
    const professional_id = row.getAttribute('professional_id');
    document.getElementById('rrequest_id').value = request_id;
    document.getElementById('professional_id').value = professional_id;
}

function close_request(button){
    open_popup('close_request');
    const row = button.closest('tr')
    const request_id = row.getAttribute('request_id');
    const customer_id = row.getAttribute('customer_id');
    document.getElementById('request_id').value = request_id;
    document.getElementById('customer_id').value = customer_id;
}

function back_button(){
    if (document.referrer) {
        window.location.href = document.referrer;
    }
    else {
        window.location.href = '/';
    }
}