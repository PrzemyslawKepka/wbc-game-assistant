### Overview
Warlords Battlecry III is a Real-Time-Strategy (RTS) computer game, where it's possible to play as one of the 16 different races. Each race can recruit different units, where each units has differents parameters and traits, making them efficent or unefficient against other units. So this application aims to help the player by showing what are the good and bad matchups for his units under his selected race and races of the enemy, allowing to quickly learn what should be the efficent strategy without remembering all the intricacies of the game.

### Usage
The application is already hosted online and can be used effectively from any device. It's available under the link:
[https://wbc-game-assistant.streamlit.app](https://wbc-game-assistant.streamlit.app)

Alternative hosting is also provided:
[https://wbc-game-assistant.onrender.com](https://wbc-game-assistant.onrender.com)

To run the app locally, the repository has to be cloned, and when all the dependencies from `requirements.txt` all installed, then it is launched by the command `streamlit run app.py` from the terminal.

Usage itself is pretty straightforward, using select boxes we choose player race and enemy races, and based on the selection we see in a graphical way what are the stats of our unit and how does it pair against enemy units.
Additionally, there also advanced options available like choosing what types of units shall be displayed, or there is a button allowing quick swap of the selected races.
Source data used in the app comes directly from the game, and also partially from external [Fandom site](https://etheria.fandom.com/wiki/Warlords_Battlecry_Wiki). Beside graphical way, data can be also browsed in tabular format under additional expander form.

<img src="https://github.com/PrzemyslawKepka/wbc_game_assistant/blob/master/app_image/wbc_game_assistant.jpg" />