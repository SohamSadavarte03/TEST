function switchForm(formId) {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signupForm').style.display = 'none';
    document.getElementById(formId).style.display = 'block';
}


function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    if (username == "user" && password == "1234") {
        document.querySelector(".usersuccessinfo").style.display = "block";
        document.querySelector(".adminsuccessinfo").style.display = "none";
    } else if (username == "admin" && password == "admin") {
        document.querySelector(".adminsuccessinfo").style.display = "block";
        document.querySelector(".usersuccessinfo").style.display = "none";
    } else {
        document.querySelector(".usersuccessinfo").style.display = "none";
        document.querySelector(".adminsuccessinfo").style.display = "none";
    }
}