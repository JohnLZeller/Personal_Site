/* ===============================================================
 * Filename: script.js
 * Author: John Zeller
 * Date Created: November 21, 2012
 * Recently Updated: November 26, 2012
 * ------
 * Notes:
 * =============================================================*/

// JAVASCRIPT FUNCTIONS

var badge_off = "<img src='images/badge.png' height ='244px' alt='hi, my name is JOHN ZELLER and I am a Software Engineer'>";
var badge_on = "<img src='images/badge-f.png' height ='244px' alt='hi, my name is JOHN ZELLER and I am a Software Engineer'>";

function onStart(){
    badge_span.innerHTML = badge_off;               // Initializes the badge
    intervalID1 = setInterval("changeBadge()",800); // Starts cycle that changes the badge every 0.8 seconds
}

function changeBadge(){
    // Uses badge_span.innerHTML to keep state
    if(badge_span.innerHTML.substring(17,26)=="badge.png"){         // If badge was off
        badge_span.innerHTML = badge_on;
    }else if(badge_span.innerHTML.substring(17,26)=="badge-f.p"){   // If badge was on
        badge_span.innerHTML = badge_off;
    }
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
    
function changeSection(choice){
    title_section.innerHTML = "<img onclick='changeSection(\"home\")' width='400px' src='images/nav/title.png'>"
    switch(choice){
        case "home":
            content_section.innerHTML = home_section;
            onStart();
            title_section.innerHTML = "";
            break;
        case "about":
            content_section.innerHTML = about_section;
            break;
        case "projects":
            content_section.innerHTML = projects_section;
            break;
        case "spacex":
            content_section.innerHTML = projects_section_spacex;
            break;
        case "marsrover":
            content_section.innerHTML = projects_section_marsrover;
            break;
        case "penny4nasa":
            content_section.innerHTML = projects_section_penny4nasa;
            break;
        case "contact":
            content_section.innerHTML = contact_section;
            break;
        default:
            break;
    }
}






// HTML SPAN CONTENT SECTIONS

var home_section = "<div id='badge'><span id='badge_span'></span></div>"

var about_section = "<div id='pic'><img height='50%' src='images/JohnZeller.jpg'></div>                                             \
    <div id='info'>                                                                                                                 \
    <p>I am a passionate Science and Technology nerd from Portland, Oregon. I enjoy talking and doing all things space,             \
    science, robotics, and business.</p>                                                                                            \
    <p>Currently a student at Oregon State University, studying Computer Science, I keep myself busy with many projects and         \
    teams. I am the Team and Software Leads of the OSU Mars Rover Team and Founder/Director of nonprofit corporation Penny4NASA.    \
    I am keen on being an integral part in making projects, with which I am involved, happen better and faster.                     \
    </p>                                                                                                                            \
    <p>Passionate about technology, science and business, I interned this summer 2012 at SpaceX as an avionics intern in hardware   \
    development.</p>                                                                                                                \
    <p>I am available for interviews, talks and always happy to meet bright people with great ideas. Contact me via email,          \
    google+, facebook, twitter or carrier pigeon.</p></div>"

var projects_section = "<div id='pic'><h2>Choose one:</h2></div>                                                                    \
     <div id='title'><a onclick='changeSection(\"spacex\");' href='javascript:void(0);'><center><h1><strong>SpaceX</strong></h1>    \
        </center></a></div>                                                                                                         \
     <div id='title'><a onclick='changeSection(\"marsrover\");' href='javascript:void(0);'><center><h1><strong>OSU Mars Rover Team  \
        </strong></h1>                                                                                                              \
        </center></a></div>                                                                                                         \
     <div id='title'><a onclick='changeSection(\"penny4nasa\");' href='javascript:void(0);'><center><h1><strong>Advocates for Space \
        Exploration / Penny4NASA</strong></h1></center></a></div>"

    var projects_section_spacex = "<div id='title'><center><h1><strong>SpaceX</strong></h1></center></div>                              \
        <a onclick='changeSection(\"projects\");' href='javascript:void(0);'><h2><< Go Back</h2></a>                                    \
        <div id='pic'><img width='400px' src='images/projects/SpaceX.jpg'><br>                                                          \
            <img width='400px' src='images/projects/SpaceX1.jpg'><br>                                                                       \
            <img width='400px' src='images/projects/SpaceX2.jpg'><br>                                                                       \
            <img width='400px' src='images/projects/SpaceX3.jpg'>                                                                           \
        </div>                                                                                                                          \
        <div id='info'>                                                                                                                 \
            <p>I interned at SpaceX during the summer of 2012. Working in Avionics in the Hardware Development test group I developed       \
            with on an off-the-shelf embedded development platform to create a framework that integrated in-house boards and                \
            allowed for interfacing with existing hardware to accomplish custom testing procedures. I also designed                         \
            and implemented an onboard Django-based server for controlling and reviewing tests in real-time.</p>                            \
            <p>The majority of this work was done in Python, with smaller portions being completed in HTML and                              \
            JavaScript.</p>                                                                                                                 \
        </div>"
    
    var projects_section_marsrover = "<div id='title'><center><h1><strong>OSU Mars Rover Team</strong></h1></center></div>              \
        <a onclick='changeSection(\"projects\");' href='javascript:void(0);'><h2><< Go Back</h2></a>                                    \
        <div id='pic'><img width='400px' src='images/projects/MarsRover.jpg'><br>                                                       \
            <img width='400px' src='images/projects/MarsRover1.jpg'><br>                                                                    \
            <img width='400px' src='images/projects/MarsRover2.jpg'><br>                                                                    \
            <img width='400px' src='images/projects/MarsRover3.jpg'>                                                                        \
        </div>                                                                                                                          \
        <div id='info'>                                                                                                                 \
            <p>This team is one of many under the OSU Robotics Club (OSURC). Our team builds a prototype rover each year with the purpose   \
            of competing in the Mars Society sponsored University Rover Challenge(URC). We design and build most of the rover from scratch, \
            using all Undergraduate and Graduate students, accessing help from professionals and professors very sparingly.</p>             \
            <p>As Team Lead, I manage weekly meetings, coordinate project leads (i.e. Mechanical, Electrical, Software, Science), organize  \
            tasks, deadlines and goals, mailing lists, secure sponsorship and recruitment activities. I also am the primary line of         \
            communication between Rover Team members, OSU, the Mars Society and OSU Robotics Club Executives. Additionally, I coordinate    \
            with our PR lead to find and attend several public events.</p>                                                                  \
            <p>As Software Lead, I manage the software design process, create deadlines, goals, and delegate tasks. I also oversee the      \
            proper implementation of software and the maintenance of repositories. Establish and use design review process for all projects.\
            </p>                                                                                                                            \
            <p>The URC requires a rover with a specified minimum functionality with emphasis on weight and cost. The rover has many         \
            systems, including but not limited to the Chassis, Robotic Arm, Communications, Video, Science, and Software</p>                \
            <p>The chassis must be structurally strong enough to withstand the rigors of the competition, have the capacity to carry the    \
            required functionality, and be optimized for minimum weight, cost, and complexity of manufacturing.</p>                         \
            <p>We do a multitude of public events to promote our team, our University and of course our sponsors. Our team has several      \
            sponsors, including NASA Oregon Space Grant, Mentor Graphics, National Science Foundation, Sunstone, Garmin, Fastenal, Stevens  \
            Water Sensor Systems, Midwest Motion Products, AJK Precision, Pacific Metal, Xerox, and 3D Connexion.</p>                       \
            <p>For more information about the OSU Mars Rover Team please <a href='http://groups.engr.oregonstate.edu/osurc/urc/'>           \
            click here</a></p>                                                                                                              \
        </div>"
    
    var projects_section_penny4nasa = "<div id='title'><center><h1><strong>Advocates for Space Exploration / Penny4NASA</strong></h1>       \
                                        </center></div>                                                                                     \
        <a onclick='changeSection(\"projects\");' href='javascript:void(0);'><h2><< Go Back</h2></a>                                    \
        <div id='pic'><img width='400px' src='images/projects/Penny4NASA.png'><br>                                                      \
            <img width='400px' src='images/projects/Penny4NASA1.jpg'><br>                                                                   \
            <img width='400px' src='images/projects/Penny4NASA2.jpg'><br><br>                                                               \
        </div>                                                                                                                          \
        <div id='info'>                                                                                                                 \
            <p>I founded Penny4NASA on March 22, 2012, and shortly after founded Advocates for Space Exploration on May 18, 2012.           \
            I have been a space enthusiast for as long as I can remember, and it's what drove me into the sciences and the field I am in    \
            today.</p>                                                                                                                      \
            <p>In mid-March of 2012 I came accross <a href='http://youtu.be/Xhc25v0DpJc'>this video</a> in which Neil deGrasse Tyson,       \
            Astrophysicist, was speaking to the U.S. Senate Committee on Commerce, Science, and Transporation about the future of the       \
            nations space program. He spoke about how important NASA was and how it was being wholly neglected in recent decades, leaving   \
            it a shred of the potential it had during the Gemini and Apollo eras. Now, I knew the importance of NASA and all STEM research, \
            but his words struck a cord with me. He went on to mention that NASA receives only one half of one-percent of the federal       \
            budget... that's 0.5%. After listening to the rest of the speech, I wanted to do something about it.</p>                        \
            <p>I founded Penny4NASA, and subsequently the nonprofit corporation Advocates for Space Exploration, to uphold the importance   \
            of Space Exploration and Science. Our organization believes wholeheartedly that our federal funding of the National Aeronautics \
            and Space Administration, at a wimpy 0.48% of the total, does not reflect the hugely important economical, technological and    \
            inspirational resource that this agency has been throughout its 50+ year history.</p>                                           \
            <p>I manage team of 20 permanent volunteers within this organization, which operates largely online using a website, social     \
            media presence, government relations, and media relations, as well as taking monetary donations. To date the organization has   \
            raised upwards of $5000 non-taxdeductible donations which has enabled the improvement of every aspect of the organization.</p>  \
        </div>"
    
var contact_section = "<div id='pic'><img height='50%' src='images/JohnZeller1.jpg'></div>                                           \
    <div id='info'><p>If you are interested in contacting me, you can find me via any of the links below to Facebook, Twitter,      \
    Google+ or Github.</p>                                                                                                          \
    <p>Perhaps the most effective means of contacting me though is by email >> <a href='mailto:johnlzeller@gmail.com'>              \
    johnlzeller@gmail.com</a></p></div>"