#!/nlp/projekty/generovani_diktatu/env/bin/python3.8

# parts of code were generated using AI tools

#imports
import sys
import cgi
import cgitb
import os
import openai
import random

from fce import get_phrases_list, choose_n_phrases, choose_n_phrases_in_order, generate_n_texts


# --------------------------------------------------------------------------------------------------------------

# random magic
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
# the warnings and errors are then explained
cgitb.enable()


# html head
print("Content-Type: text/html; charset=utf-8\n\n")
print("<html>")
print("<head>")
print("<title>Generátor diktátů</title>")
# add bootstrap
print('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous" >')

print(
"""
<style>
/* Popup container - can be anything you want */
.popup {
  position: relative;
  display: inline-block;
  cursor: pointer;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* The actual popup */
.popup .popuptext {
  visibility: hidden;
  width: 160px;
  background-color: #555;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 8px 0;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -80px;
}

/* Popup arrow */
.popup .popuptext::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #555 transparent transparent transparent;
}

/* Toggle this class - hide and show the popup */
.popup .show {
  visibility: visible;
  -webkit-animation: fadeIn 1s;
  animation: fadeIn 1s;
}

/* Add animation (fade in the popup) */
@-webkit-keyframes fadeIn {
  from {opacity: 0;} 
  to {opacity: 1;}
}

@keyframes fadeIn {
  from {opacity: 0;}
  to {opacity:1 ;}
}
</style>
"""
)

print("</head>")
print("<body>")

# JAVASCRIPT FUNCTIONS
print(
"""
<script type="text/javascript" language="JavaScript">
<!--
// Function which copies to clipboard
const copyToClipboard = async (elementSelector) => {
  try {
    const element = document.querySelector(elementSelector);
    if (!element) {
      throw new Error("Element not found");
    }
    await navigator.clipboard.writeText(element.textContent);
  } catch (error) {
    console.error("Failed to copy to clipboard:", error);
  }
}

// Function to attach onclick event handler to buttons; to handle multiple buttons and fields
const attachButtonClickHandler = (buttonSelector, elementSelector) => {
  const button = document.querySelector(buttonSelector);
  if (button) {
    button.addEventListener('click', () => copyToClipboard(elementSelector));
  } else {
    console.error("Button not found:", buttonSelector);
  }
}

function reloadPage() {
    location.reload();
}

// If jev = shoda is chosen, disables the possibility to choose difficulty level
function disableDiffOnShoda() {
    var isChecked = document.getElementById("shoda").checked
    
    // Select all radio buttons with the name "diff"
    const radioButtons = document.querySelectorAll("input[name='diff']");

    // Loop through each radio button
    radioButtons.forEach(button => {
        button.disabled = isChecked;
    });
}

//-->
</script>
"""
)


# global variables
os.environ['OPENAI_API_KEY'] = "insert_your_private_key"
base_path = "/mnt/silenos/silenos1/nlp/projekty/generovani_diktatu"
client = openai.OpenAI()
model = "gpt-3.5-turbo"


# Get form data  
form = cgi.FieldStorage()

print('<div class="p-3 fs-4 text-primary-emphasis bg-primary-subtle border border-primary-subtle"> Nástroj na generování diktátů</div>')

# the parameters have been chosen, creating request, sending it to OpenAI, then displaying results
if form:
    
    jev = form["jev"].value
    length = form["length"].value
    
    n_of_phrases_dict = {"30": 5, "40": 6, "50": 7}
    diff_number_to_word = {"0" : "lehčí", "1" : "těžší", "2": "mix"}
    jev_to_name = {"b": "vyjmenovaná slova po B", "l": "vyjmenovaná slova po L", "m": "vyjmenovaná slova po M",
                   "p": "vyjmenovaná slova po P", "s":"vyjmenovaná slova po S", "v": "vyjmenovaná slova po V",
                   "shoda": "shoda podmětu v množném čísle s přísudkem v minulém čase", "ěje": "psaní ě, je, mně/mě po b, p, v, m"
                   }
    length_to_length = {"30": 37, "40": 45, "50": 55}   # protože chatGPT spíš zkracuje
    
    file_name=random.choice(os.listdir(f"{base_path}/zdroje_{jev}"))
    
    phrases_list = get_phrases_list(f"{base_path}/zdroje_{jev}/{file_name}")
    
    if jev == "shoda":      # ve cvičeních na shodu se neřeší obtížnost a model zpracovává vybraná slovní spojení v pořadí, v jakém je dostal
        chosen = choose_n_phrases_in_order(phrases_list, n_of_phrases_dict[str(length)])
        generated_texts = generate_n_texts(chosen, length_to_length[length], model, client, True)
        
        print(f'<div class="row ms-3">Zobrazuju návrhy na diktáty podle vybraných požadavků ({jev_to_name[jev]}, {length} slov).</div>')
        
    else:
        diff = form["diff"].value
        chosen = choose_n_phrases(diff, phrases_list, n_of_phrases_dict[str(length)])
        generated_texts = generate_n_texts(chosen, length_to_length[length], model, client)
        
        print(f'<div class="row ms-3">Zobrazuju návrhy na diktáty podle vybraných požadavků ({jev_to_name[jev]}, {length} slov,  obtížnost {diff_number_to_word[str(diff)]}).</div>')
    
    print('<div class="row ms-3">Ke generování byla použita tato slovní spojení:</div>')
    print('<div class="row ms-5 mb-3">')
    for i in range(len(chosen)):
        if i < len(chosen)-1:
            print(chosen[i], end="; ")
        else:
            print(chosen[i], end=".")
    print("</div>")
    
    for i, text in enumerate(generated_texts):
        print('<div class="row ms-1 mb-3">')
        print('<div class="col">')
        print(f'<div id="diktat{i}" class="card card-body">{text} ({len(text.split())} slov)</div>')
        print("</div>")
        print('<div class="col-6 my-auto">')
        print(f'<button id="button{i}" class="btn btn-primary btn-sm">Kopírovat diktát</button>')
        print("</div>")
        print("</div>")
    print('<div class="row ms-1">')
    print('<div class="col">')
    print('<button onclick="reloadPage()" class="btn btn-primary">Vygenerovat znovu</button>')
    print('<a href="app.cgi" class="btn btn-primary">Zpět na výběr</a>')        # pošle odkaz sama na sebe s metodou get a tím pádem se nepošlou data z formu a tím pádem se to vrátí na stránku s výběrem - asi
    print("</div>")

        
# Attach click event handlers to buttons
    print(
    """
    <script type="text/javascript" language="JavaScript">
    <!--
        for (let i = 0; i < """ + str(len(generated_texts)) + """; i++) {
            attachButtonClickHandler(`#button${i}`, `#diktat${i}`);
        }

    //-->
    </script>
    """
    )

# ----------------
# the parameters for dictation exercise have not been not chosen yet
else:
    print(
"""
<div class="container ms-3">
    <!-- všechno jeden řádek -->
    <div class="row">
        <!-- výběr a submit button -->
        <div class="col">
          <form method="post" action="app.cgi" id="theForm">
                <div class="row mt-2">
                    <div class="col">Vyberte si pravopisný jev na procvičení</div>
                </div>
                <div class="row mb-3">
                    <div class="col ms-3">
                        <input type="radio" id="ěje" name="jev" value="ěje" onclick="disableDiffOnShoda()">
                        <label for="ěje">Psaní ě, je, mně/mě po b, p, v, m</label><br> 

                        <input type="radio" id="shoda" name="jev" value="shoda" onclick="disableDiffOnShoda()">
                        <label for="shoda">
                            <div>
                            Shoda podmětu v množném čísle s přísudkem v minulém čase
                                <div class="popup" onclick="popUpFunction1()">
                                    <img src="info_icon.jpg" width="15" height="15" alt="Info icon, click it">
                                    <span class="popuptext" id="popup1">S touto volbou není možné zvolit obtížnost diktátu.</span>
                                </div>
                            </div>
                        </label><br> 

                        <input type="radio" id="b" name="jev" value="b" onclick="disableDiffOnShoda()">
                        <label for="b">Vyjmenovaná slova po B</label><br>    

                        <input type="radio" id="l" name="jev" value="l" onclick="disableDiffOnShoda()">
                        <label for="l">Vyjmenovaná slova po L</label><br>

                        <input type="radio" id="m" name="jev" value="m" onclick="disableDiffOnShoda()">
                        <label for="m">Vyjmenovaná slova po M</label><br>

                        <input type="radio" id="p" name="jev" value="p" onclick="disableDiffOnShoda()">
                        <label for="p">Vyjmenovaná slova po P</label><br>

                        <input type="radio" id="s" name="jev" value="s" onclick="disableDiffOnShoda()">
                        <label for="s">Vyjmenovaná slova po S</label><br>

                        <input type="radio" id="v" name="jev" value="v" onclick="disableDiffOnShoda()">
                        <label for="v">Vyjmenovaná slova po V</label><br>
                    </div>
                </div>
          
                <div class="row">
                    <div class="col">Vyberte si délku diktátu</div>
                </div>
                <div class="row mb-3">
                    <div class="col ms-3">
                        <input type="radio" id="len_short" name="length" value=30>
                        <label for="len_short">30 slov</label><br>      
                        <input type="radio" id="len_medium" name="length" value=40>
                        <label for="len_medium">40 slov</label><br>
                        <input type="radio" id="len_long" name="length" value=50>
                        <label for="len_long">50 slov</label><br>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col">Vyberte si obtížnost diktátu</div>
                </div>
                <div class="row mb-3">
                    <div class="col ms-3">
                        <input type="radio" id="diff_easy" name="diff" value=0>
                        <label for="diff_easy">lehčí</label><br>      
                        <input type="radio" id="diff_hard" name="diff" value=1>
                        <label for="diff_hard">těžší</label><br>
                        <input type="radio" id="diff_mix" name="diff" value=2>
                        <label for="diff_mix">mix
                            <div class="popup" onclick="popUpFunction2()">
                                <img src="info_icon.jpg" width="15" height="15" alt="Info icon, click it">
                                <span class="popuptext" id="popup2">Lehčí i těžší dohromady</span>
                            </div>
                    </label><br>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col">
                        <button type="submit" class="btn btn-primary">Vygenerovat</button>
                    </div>
                </div>
            </form>
        </div>
        
        <!-- tlačítka a rozbalování -->
        <div class="col">
            <div class="row">
                <div class="col">
                    <button class="btn btn-primary mt-2 dropdown-toggle" type="button" id="whatButton">
                        Co to je
                    </button>
                    <button class="btn btn-primary mt-2 dropdown-toggle" type="button" id="howButton">
                        Jak to používat
                    </button>
                </div>
            </div>
            
            <div class="row">
                <div class="col">
                    <div class="card card-body" id="what" style="display:none;">
                        Nástroj slouží ke generování diktátů. Generují se souvislé texty o dané délce a obtížnosti. Texty obsahují slova procvičující vybraný pravopisný jev. Diktáty jsou určeny primárně pro žáky na prvním stupni ZŠ.<br>
                        Vytváření diktátů je poloautomatické. Z ručně vytvořené databáze slovních spojení se určitým způsobem nějaká vyberou a ty se předají ChatGPT, aby je spojil do souvislého vyprávění. Znamená to, že každý diktát je svým způsobem unikátní. Znamená to ale také, že v textu mohou být drobné syntaktické nebo sémantické nepřesnosti.<br>
                        Předpoklad je takový, že po pár drobných úpravách je možné diktáty použít pro výuku. Nástroj by tak měl zkrátit čas potřebný k hledání nebo vymýšlení vhodného diktátu.<br>
                        Webová stránka je výsledkem mé bakalářské práce.
                    </div>
                    <div class="card card-body" id="how" style="display:none;">
                        Nastavte si, jak parametry chcete použít pro generování diktátu. Klikněte na tlačítko Vygenerovat a chvíli počkejte (cca 10 sekund). Poté se vám na nové stránce zobrazí tři diktáty vytvořené podle daných požadavků a slovní spojení, která ke tvorbě diktátu byla použita.<br>
                        Pokud je vybrané procvičování shody podmětu s přísudkem, není možné si už vybrat obtížnost diktátu. Je to tak proto, že jsou všechny možnosti podobně obtížné.<br>
                        Nezkoušejte prosím používat stránku jinak, než jak je myšleno. Je dost pravděpodobné, že vám to vyhodí nějakou chybu. Pokud se tak stane, zavřete a otevřte ji znova nebo zkuste tlačítko zpět:)
                    </div>
                </div>
            </div>
        </div>
    </div>            
</div>

"""
)
      
print(
"""
<script type="text/javascript" language="JavaScript">
<!--
// show/hide div on click and hide the other if displayed - WHAT
document.getElementById("whatButton").onclick = function() {
    var whatDiv = document.getElementById("what");
    if (whatDiv.style.display === "none") {
        whatDiv.style.display = "block";
    } else {
        whatDiv.style.display = "none";
    }
    
    //hide the other if displayed
    var howDiv = document.getElementById("how");
    if (howDiv.style.display === "block") {
        howDiv.style.display = "none";
    } 
};

// show/hide div on click hide the other if displayed - HOW
document.getElementById("howButton").onclick = function() {
    var howDiv = document.getElementById("how");
    if (howDiv.style.display === "none") {
        howDiv.style.display = "block";
    } else {
        howDiv.style.display = "none";
    }
    
    //hide the other if displayed
    var whatDiv = document.getElementById("what");
    if (whatDiv.style.display === "block") {
        whatDiv.style.display = "none";
    }
};

// When the user clicks on div, open the popup
function popUpFunction1() {
  var popup = document.getElementById("popup1");
  popup.classList.toggle("show");
}

function popUpFunction2() {
  var popup = document.getElementById("popup2");
  popup.classList.toggle("show");
}

//-->
</script>
""")      

print('<div class="text-sm-end me-3 mt-3" >© Jan Malý, 2024.</div>')
print("</body>")
print("</html>")
