/* ===============================================================
 * Filename: script.js
 * Author: John Zeller
 * Date Created: November 21, 2012
 * Recently Updated: November 27, 2012
 * ------
 * Notes:
 * =============================================================*/

// JAVASCRIPT FUNCTIONS

function onStart(){
    $('#footer').load('footer.html');
    $('#navbar').load('footer.html');
}

function changeIcon(element, icon, on_off){
    switch(icon){
        case "fb":
            if(on_off=="on"){
                element.src="images/icons/fb-h.png"
            }else if(on_off=="off"){
                element.src="images/icons/fb.png"
            }else if(on_off=="click"){
                element.src="images/icons/fb-c.png"
            }
            break;
        case "tw":
            if(on_off=="on"){
                element.src="images/icons/tw-h.png"
            }else if(on_off=="off"){
                element.src="images/icons/tw.png"
            }else if(on_off=="click"){
                element.src="images/icons/tw-c.png"
            }
            break;
        case "gp":
            if(on_off=="on"){
                element.src="images/icons/gp-h.png"
            }else if(on_off=="off"){
                element.src="images/icons/gp.png"
            }else if(on_off=="click"){
                element.src="images/icons/gp-c.png"
            }
            break;
        case "linkedin":
            if(on_off=="on"){
                element.src="images/icons/linkedin.png"
            }else if(on_off=="off"){
                element.src="images/icons/linkedin.png"
            }else if(on_off=="click"){
                element.src="images/icons/linkedin.png"
            }
            break;
        case "git":
            if(on_off=="on"){
                element.src="images/icons/git-h.png"
            }else if(on_off=="off"){
                element.src="images/icons/git.png"
            }else if(on_off=="click"){
                element.src="images/icons/git-c.png"
            }
            break;
        case "rs":
            if(on_off=="on"){
                element.src="images/icons/rs-h.png"
            }else if(on_off=="off"){
                element.src="images/icons/rs.png"
            }else if(on_off=="click"){
                element.src="images/icons/rs-c.png"
            }
            break;
        case "about":
            if(on_off=="on"){
                element.src="images/nav/About-h.png"
            }else if(on_off=="off"){
                element.src="images/nav/About.png"
            }
            break;
        case "projects":
            if(on_off=="on"){
                element.src="images/nav/Projects-h.png"
            }else if(on_off=="off"){
                element.src="images/nav/Projects.png"
            }
            break;
        case "contact":
            if(on_off=="on"){
                element.src="images/nav/Contact-h.png"
            }else if(on_off=="off"){
                element.src="images/nav/Contact.png"
            }
            break;
        default:
            break;
    }
}