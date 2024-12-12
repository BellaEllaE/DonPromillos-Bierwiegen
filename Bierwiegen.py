# Bierwiegen.py
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.widget import Widget

class PlayerScreen(Screen):
    players = ListProperty([])  # [name, weight, points]
    
    def add_player(self, name):
        if name.strip():
            # [name, current_weight, points, [weight_history]]
            self.players.append([name.strip(), 0, 0, []])  # weight_history hinzugefügt
            self.ids.player_name.text = ''
            self.update_player_list()
            return True
        return False

    def remove_player(self, player_name):
        for player in self.players[:]:  # Kopie der Liste durchlaufen
            if player[0] == player_name:
                self.players.remove(player)
                self.update_player_list()
                self.show_popup(f"Spieler {player_name} wurde entfernt!")
                return

    def update_player_list(self):
        # Spielerliste-Widget leeren und neu befüllen
        player_list = self.ids.player_list
        player_list.clear_widgets()
        for player in self.players:
            # Container für Spielername und Lösch-Button
            container = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp')
            
            # Spielername Label
            name_label = Label(text=player[0], size_hint_x=0.7)
            
            # Lösch-Button
            delete_button = Button(
                text='Löschen',
                size_hint_x=0.3,
                on_release=lambda x, name=player[0]: self.remove_player(name)
            )
            
            container.add_widget(name_label)
            container.add_widget(delete_button)
            player_list.add_widget(container)

    def start_game(self):
        if len(self.players) < 2:
            self.show_popup("Mindestens 2 Spieler werden benötigt!", "Fehler")
            return False
        return True

    def show_popup(self, text, title="Erfolg"):
        popup = Popup(title=title,
                     content=Label(text=text),
                     size_hint=(None, None), size=(400, 200))
        popup.open()

class WeightScreen(Screen):
    current_player_index = NumericProperty(0)
    current_player_name = StringProperty("")

    def on_enter(self):
        self.current_player_index = 0
        self.update_current_player()

    def update_current_player(self):
        if self.current_player_index < len(self.manager.get_screen('player').players):
            self.current_player_name = self.manager.get_screen('player').players[self.current_player_index][0]

    def save_weight(self, weight_str):
        try:
            weight = float(weight_str)
            if weight > 1500:
                self.show_popup("Gewicht muss unter 1500g sein!", "Fehler")
                return
            
            players = self.manager.get_screen('player').players
            players[self.current_player_index][1] = weight  # Aktuelles Gewicht
            players[self.current_player_index][3].append(weight)  # Zur Historie hinzufügen
            self.current_player_index += 1
            
            self.ids.weight_input.text = ''
            
            if self.current_player_index < len(players):
                self.update_current_player()
            else:
                self.manager.current = 'overview'
        except ValueError:
            self.show_popup("Bitte geben Sie eine gültige Zahl ein!", "Fehler")


    def show_popup(self, text, title="Fehler"):
        popup = Popup(title=title,
                     content=Label(text=text),
                     size_hint=(None, None), size=(400, 200))
        popup.open()

class OverviewScreen(Screen):
    def on_enter(self):
        self.ids.overview_box.clear_widgets()
        players = self.manager.get_screen('player').players
        drinking_screen = self.manager.get_screen('drinking')
        
        # Zielgewichte anzeigen
        if hasattr(drinking_screen, 'target_weights') and drinking_screen.target_weights:
            target_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height='80dp',
                padding='10dp',
                spacing='10dp'
            )
            
            target_label = Label(
                text="Zielgewichte:",
                bold=True,
                size_hint_y=None,
                height='30dp'
            )
            target_box.add_widget(target_label)
            
            # Zielgewichte mit Pfeilen verbinden
            targets_text = ""
            for i, target in enumerate(drinking_screen.target_weights):
                targets_text += f"{target:.1f}g"
                if i < len(drinking_screen.target_weights) - 1:
                    targets_text += " → "
            
            weights_label = Label(
                text=targets_text,
                size_hint_y=None,
                height='30dp'
            )
            target_box.add_widget(weights_label)
            
            self.ids.overview_box.add_widget(target_box)
            
            # Trennlinie nach den Zielgewichten
            separator = Label(
                text='_' * 50,
                size_hint_y=None,
                height='20dp'
            )
            self.ids.overview_box.add_widget(separator)
        
        for player in players:
            # Container für jeden Spieler
            player_box = BoxLayout(
                orientation='vertical', 
                size_hint_y=None, 
                height='100dp',
                padding='10dp',
                spacing='10dp'
            )
            
            # Spielername und Punkte
            name_label = Label(
                text=f"{player[0]} (Punkte: {player[2]})",
                bold=True,
                size_hint_y=None,
                height='30dp'
            )
            player_box.add_widget(name_label)
            
            # Gewichte-Historie
            weights_text = "Gewichte: "
            for i, weight in enumerate(player[3]):
                weights_text += f"{weight:.1f}g"
                if i < len(player[3]) - 1:
                    weights_text += " → "
            
            weights_label = Label(
                text=weights_text,
                size_hint_y=None,
                height='30dp'
            )
            player_box.add_widget(weights_label)
            
            # Zum Hauptcontainer hinzufügen
            self.ids.overview_box.add_widget(player_box)
            
            # Einfache Trennlinie (Label statt Widget)
            if player != players[-1]:  # Keine Linie nach dem letzten Spieler
                separator = Label(
                    text='_' * 50,  # Unterstrich als Trennlinie
                    size_hint_y=None,
                    height='20dp'
                )
                self.ids.overview_box.add_widget(separator)
    def end_game(self):
        self.manager.current = 'end'

class DrinkingScreen(Screen):
    target_weight = NumericProperty(0)

    def start_drinking(self, target_weight):
        try:
            new_target = float(target_weight)
            
            # Prüfen ob es das erste Zielgewicht ist
            if not hasattr(self, 'target_weights'):
                self.target_weights = []
            
            # Prüfen ob das neue Zielgewicht kleiner/gleich dem letzten ist
            if self.target_weights and new_target > self.target_weights[-1]:
                self.show_popup(f"Neues Zielgewicht muss kleiner oder gleich dem letzten Zielgewicht ({self.target_weights[-1]}g) sein!", "Fehler")
                return
                
            self.target_weight = new_target
            self.target_weights.append(self.target_weight)
            
            self.ids.input_area.opacity = 0
            self.ids.drink_label.text = f"TRINKT AUF: {self.target_weight}g!"
            self.ids.drink_label.font_size = '36sp'
            Clock.schedule_once(self.finish_drinking, 4)
        except ValueError:
            self.show_popup("Bitte geben Sie eine gültige Zahl ein!", "Fehler")

    def finish_drinking(self, dt):
        self.manager.current = 'new_weight'
        # Eingabefeld und Button für nächstes Mal wieder sichtbar machen
        self.ids.input_area.opacity = 1
        
    def on_enter(self):
        # Beim Betreten des Screens alles sichtbar machen
        if hasattr(self.ids, 'input_area'):
            self.ids.input_area.opacity = 1

class NewWeightScreen(Screen):
    current_player_index = NumericProperty(0)
    current_player_name = StringProperty("")
    target_weight = NumericProperty(0)

    def on_enter(self):
        self.current_player_index = 0
        self.update_current_player()
        self.target_weight = self.manager.get_screen('drinking').target_weight

    def update_current_player(self):
        if self.current_player_index < len(self.manager.get_screen('player').players):
            self.current_player_name = self.manager.get_screen('player').players[self.current_player_index][0]

    def save_new_weight(self, weight_str):
        try:
            new_weight = float(weight_str)
            players = self.manager.get_screen('player').players
            current_player = players[self.current_player_index]
            
            # Prüfen ob der Spieler schon Gewichte hat
            if current_player[3]:  # Überprüfe die weight_history
                last_weight = current_player[3][-1]
                if new_weight > last_weight:
                    self.show_popup(
                        f"Neues Gewicht ({new_weight}g) muss kleiner oder gleich dem letzten Gewicht ({last_weight}g) sein!", 
                        "Fehler"
                    )
                    return
            
            # Wenn die Validierung erfolgreich war, Gewicht speichern
            current_player[1] = new_weight
            current_player[3].append(new_weight)
            self.current_player_index += 1
            
            self.ids.new_weight.text = ''
            
            if self.current_player_index < len(players):
                self.update_current_player()
            else:
                self.determine_winner()
        except ValueError:
            self.show_popup("Bitte geben Sie eine gültige Zahl ein!", "Fehler")

    def determine_winner(self):
        players = self.manager.get_screen('player').players
        target = self.manager.get_screen('drinking').target_weight
        
        min_diff = float('inf')
        winners = []
        
        for player in players:
            diff = abs(player[1] - target)
            if diff < min_diff:
                min_diff = diff
        
        for player in players:
            if abs(player[1] - target) == min_diff:
                winners.append(player)
                player[2] += 1
        
        if len(winners) == 1:
            winner_text = f"Glückwunsch {winners[0][0]}!"
        else:
            winner_names = [winner[0] for winner in winners]
            winner_text = "Glückwunsch " + " und ".join(winner_names) + "!"
        
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=winner_text))
        content.add_widget(Label(text=f"Abstand zum Zielgewicht: {min_diff:.1f}g"))
        
        popup = Popup(title='Gewinner!',
                     content=content,
                     size_hint=(None, None), size=(400, 200))
        popup.bind(on_dismiss=lambda x: self.return_to_overview())
        popup.open()

    def return_to_overview(self):
        self.manager.current = 'overview'

    def show_popup(self, text, title="Fehler"):
        popup = Popup(title=title,
                     content=Label(text=text),
                     size_hint=(None, None), size=(400, 200))
        popup.open()

class EndScreen(Screen):
    def on_enter(self):
        players = self.manager.get_screen('player').players
        winner = max(players, key=lambda x: x[2])
        
        # Gewinner-Label aktualisieren
        self.ids.winner_label.text = f"Gewinner: {winner[0]}\nmit {winner[2]} Punkten!"

    def new_game(self):
        # Spielerliste zurücksetzen
        self.manager.get_screen('player').players.clear()
        # Zum Start-Bildschirm wechseln
        self.manager.current = 'player'

    def quit_app(self):
        App.get_running_app().stop()

class DrinkingGameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PlayerScreen(name='player'))
        sm.add_widget(WeightScreen(name='weight'))
        sm.add_widget(OverviewScreen(name='overview'))
        sm.add_widget(DrinkingScreen(name='drinking'))
        sm.add_widget(NewWeightScreen(name='new_weight'))
        sm.add_widget(EndScreen(name='end'))
        return sm

if __name__ == '__main__':
    DrinkingGameApp().run()