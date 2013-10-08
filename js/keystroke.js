/* ===============================================================
 * Filename: keystroke.js
 * Author: John Zeller
 * Date Created: October 7, 2013
 * Recently Updated: October 7, 2013
 * ------
 * Notes:
 * =============================================================*/

// Adding some key stroke functionality

 var intro = true;
$(window).keyup(function(event){
    if ((event.keyCode == 89) && (intro == true)){
        $('#sidebar, #main-nav, #footer').fadeIn('slow');
        $('#badge').fadeOut('slow');
        setTimeout(function(){$('#content').fadeIn('slow')}, 1000);
        intro = false;
    }else if ((event.keyCode == 78) && (intro == true)){
        alert("WARNING: User could not detect rhetorical question. Overriding user...");
        $('#sidebar, #main-nav, #footer').fadeIn('slow');
        $('#badge').fadeOut('slow');
        setTimeout(function(){$('#content').fadeIn('slow')}, 1000);
        intro = false;
    }
});

function yes(){
    $('#sidebar, #main-nav, #footer').fadeIn('slow');
    $('#badge').fadeOut('slow');
    setTimeout(function(){$('#content').fadeIn('slow')}, 1000);
}
function no(){
    alert("WARNING: User could not detect rhetorical question. Overriding user...");
    $('#sidebar, #main-nav, #footer').fadeIn('slow');
    $('#badge').fadeOut('slow');
    setTimeout(function(){$('#content').fadeIn('slow')}, 1000);
}