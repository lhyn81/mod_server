
$(document).ready(function() {
  gohome();
});

function gohome(){
  $("div[data-role='content']").hide();
  $("#content_home").show();
}

function showmodlist(){
  $("div[data-role='content']").hide();
  $("#content_modlist").show();
}

function test(){
  $("#content_mod").load("/mobile/test");
  $("#footbar").html("<ul>"+
      "<li><a href='#' onclick='gohome()' data-icon='home'>首页</a></li>"+
      "<li><a href='#' data-icon='star'>发现</a></li>"+
      "<li><a href='#' data-icon='grid'>我的</a></li>"+
      "</ul>"
    );
  $("div[data-role='content']").hide();
  $("#content_mod").show();
}

function showinfo(){
  $("#div_info").show();
  $("#div_input").hide();
  $("#div_rlt").hide();
}

function showinput(){
  $("#div_info").hide();
  $("#div_input").show();
  $("#div_rlt").hide();
}

function showrlt(){
  $("#div_info").hide();
  $("#div_input").hide();
  $("#div_rlt").show();
}


