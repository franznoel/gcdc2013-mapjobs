// jquery validation for form-signup
$('#form-signup').validate({
  rules : {
    account : { required : true, },
    name : { required : true, },
    email : { required : true, email : true},
  },
  messages : {
    account : { required : "The account is a required field", },
    name : { required : "The company name is a required field", },
    email : { required : "The e-mail is a required field", email : "Email should be in email format"},
  },
  submitHandler : function(form) {
    form.submit()
  }
});

// jquery validation for form-login
$('#form-login').validate({
  rules : {
    account : {required : true, },
    username : { required : true },
    password : { required : true },
  },
  messages : {
    account : { required : "The company_name field is required.", },
    username : { required : "The username field is required.", },
    password : { required : "The password field is required.</p>", }
  },
  submitHandler : function(form) {
    form.submit();
  }
});









