# Create your views here.
# import statements
import random
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from .models import *
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import *
from django.contrib.auth.views import LoginView

# from plotly (for team type graphing)
# import plotly
# import plotly.graph_objs as go

# Class to show the home page
class ShowHome(TemplateView):
    ''' class to connect home URL to correct HTML template '''
    template_name = "exo/show_home.html"

class CreateProfileView(View):
    ''' class to handle user and profile creation '''
    def get(self, request):
        user_form = UserCreationForm()
        profile_form = CreateProfilesForm()
        return render(request, "exo/signup.html", {
            "user_form": user_form,
            "profile_form": profile_form
        })

    def post(self, request):
        user_form = UserCreationForm(request.POST)
        profile_form = CreateProfilesForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            login(request, user)  # Log in the new user
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect(reverse("profile", kwargs={"pk": profile.pk}))

        return render(request, "exo/signup.html", {
            "user_form": user_form,
            "profile_form": profile_form
        })
    
class CustomLoginView(LoginView):
    template_name = 'exo/login.html'

    def get_success_url(self):
        return reverse('profile', kwargs={'pk': Profiles.objects.get(user=self.request.user).pk
})

class ShowProfileView(DetailView, LoginRequiredMixin):
    ''' show the current users profile '''
    model = Profiles
    template_name = "exo/profile.html"
    context_object_name = "profile"

class PlanetView(DetailView):
    ''' class to view an individual planet screen '''
    model = Planet
    template_name = "exo/show_planet.html"
    context_object_name = "planet"

class PlanetArchive(ListView):
    ''' class to show an archive of ALL planets '''
    model = Planet
    template_name = "exo/planet_archive.html"
    context_object_name = "planets"

    def get_queryset(self):
        '''' gets the resulting query set from the filtered planets '''
        results = super().get_queryset()

        # filter out results based on what was in the user's request
        if 'type' in self.request.GET:
            planet_t = self.request.GET['type']
            if planet_t:
                results = results.filter(p_type=planet_t)

        return results

class UpdateProfile(LoginRequiredMixin, UpdateView):
    ''' class to update an existing profile infor '''
    model = Profiles
    form_class = UpdateProfileForm
    template_name = "exo/update_profile_form.html"

    def get_object(self):
        ''' returns the correct profile instance for the current user '''
        prof = Profiles.objects.get(user=self.request.user)
        return prof
    
    def get_success_url(self):
        ''' determine where to go after the operation '''
        self_obj = self.get_object()
        pks = self_obj.pk
        return reverse('profile', kwargs={'pk': pks })
    
    # get login url...
    def get_login_url(self) -> str:
        '''return the URL required for login (before this step)'''
        return reverse('login')

class DeletePlanet(LoginRequiredMixin, DeleteView):
    ''' class to delete an existing user planet '''
    model = Planet
    template_name = "exo/delete_planet_form.html"
    context_object_name = "planet"

    # get success url
    def get_success_url(self):
        ''' provide a place to go after deleting the planet '''
        pk = self.kwargs['pk']
        planet = Planet.objects.get(pk=pk)
        return reverse('profile', kwargs={'pk': planet.profile.pk })

    # get login url
    def get_login_url(self) -> str:
        '''return the URL required for login (before this step)'''
        return reverse('login')
    
class Leaderboard(TemplateView):
    ''' class to show the leaderboard screen and its context '''
    template_name = "exo/leaderboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_planets = list(Planet.objects.all())
        top_earth_similarity = sorted(
            all_planets,
            key=lambda p: p.earth_like(),
            reverse=True
        )[:5]

        # Sort by model fields using ORM
        top_mass = Planet.objects.order_by('-mass')[:5]
        top_gravity = Planet.objects.order_by('-gravity')[:5]

        context.update({
            'top_earth_similarity': top_earth_similarity,
            'top_mass': top_mass,
            'top_gravity': top_gravity,
        })

        return context



# def signup(request):
    # if request.method == "POST":
        # form = UserCreationForm(request.POST)
        # if form.is_valid():
            # form.save()
            # return redirect('login')
    # else:
        # form = UserCreationForm()
    # return render(request, 'exo/signup.html', {"form": form})

def start_game(request):
    return render(request, 'exo/start_game.html')

# @login_required
# def profile(request):
    # return render(request, 'exo/profile.html', {'user': request.user})

COMPOSITIONS = ["Nitrogen", "Oxygen", "Carbon Dioxide", "Hydrogen", "Helium", "Argon", "Methane", "Neon", "Sulfur Dioxide", "Carbon Monoxide", "None"]

P_TYPES = ["Terrestrial", "Gas Giant", "Ice Giant", "Ocean Planet", "Mini-Neptune", "Dyson-Sphere"]
P_TYPE_PROB = [0.35, 0.25, 0.18, 0.1, 0.1, 0.02]

ATMOS_PROBS = {
  "Terrestrial": [0.60,0.15,0.03,0.01,0.01,0.03,0.01,0.01,0.01,0.01,0.12],
  "Gas Giant":  [0.01,0.01,0.01,0.38,0.40,0.01,0.10,0.02,0.01,0.01,0.04],
  "Ice Giant":  [0.01,0.01,0.01,0.12,0.56,0.01,0.20,0.05,0.01,0.01,0.01],
  "Ocean Planet":[0.40,0.25,0.15,0.01,0.01,0.05,0.01,0.01,0.05,0.05,0.01],
  "Mini-Neptune":[0.02,0.01,0.01,0.28,0.50,0.01,0.12,0.01,0.01,0.01,0.02],
  "Dyson-Sphere":[0,0,0,0,0,0,0,0,0,0,1.0]
}

MASS_RANGES = {
    "Terrestrial": (0.1, 3.0),    
    "Gas Giant": (50.0, 300.0), 
    "Ice Giant": (10.0, 50.0),
    "Ocean Planet": (0.5, 3.0),    
    "Mini-Neptune": (2.0, 10.0),   
    "Dyson-Sphere": (1000.0, 5000.0), }

RADIUS_RANGES = {
    "Terrestrial": (0.8, 1.5),
    "Gas Giant": (8, 15),
    "Ice Giant": (3, 6),
    "Ocean Planet": (1, 2),
    "Mini-Neptune": (2, 4),
    "Dyson-Sphere": (1000, 5000), 
}

G_CONST = 9.8

NAME_PREFIXES = ["Astra", "Nova", "Vortex", "Zenith", "Orion", "Luna", "Eclipse", "Nebula", "Solara", "Galaxis"]

def weighted_sample_without_replacement(elements, weights, k):
    assert k <= len(elements), "Cannot sample more elements than available"
    elements_and_weights = list(zip(elements, weights))
    selected = []

    # Make a copy so we don't modify original
    elems_weights = elements_and_weights[:]

    for _ in range(k):
        total_weight = sum(w for e, w in elems_weights)
        pick = random.uniform(0, total_weight)
        cumulative = 0
        for i, (e, w) in enumerate(elems_weights):
            cumulative += w
            if pick <= cumulative:
                selected.append(e)
                # Remove selected so no repeats
                elems_weights.pop(i)
                break
    return selected

@login_required
def generate_random_planet(request):
    profile = get_object_or_404(Profiles, user=request.user)

    p_type = random.choices(P_TYPES, weights=P_TYPE_PROB, k=1)[0]

    probabilities = ATMOS_PROBS[p_type]
    comp = weighted_sample_without_replacement(COMPOSITIONS, probabilities, 3)    
    mass_min, mass_max = MASS_RANGES[p_type]
    mass = round(random.uniform(mass_min, mass_max), 2)
    # helper for gravity calculation
    radius = random.uniform(*RADIUS_RANGES[p_type])
    gravity = round(G_CONST * (mass / (radius ** 2)), 2)
    name = f"{random.choice(NAME_PREFIXES)}-{random.randint(1000, 9999)}"
   

    planet = Planet.objects.create(
        profile=profile,
        designation=name,
        mass=mass,
        gravity=gravity,
        p_type = p_type,
        comp=comp,
    )

    return redirect('show_planet', pk=planet.pk)

import random
from typing import Dict, Tuple, Optional
from django.shortcuts import render, redirect

# ----- Game config -----
WIN_TARGET = 2  # best of three → first to 2 round wins
BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}


# ----- Helpers -----
def _new_type_map() -> Dict[int, str]:
    """
    Create a fresh random assignment of numbers 1..9 into three types:
    3 numbers → rock, 3 → paper, 3 → scissors.
    Example: {2:'rock', 7:'rock', 9:'rock', 1:'paper', ...}
    """
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    type_map: Dict[int, str] = {}
    for i, n in enumerate(numbers):
        if i < 3:
            type_map[n] = "rock"
        elif i < 6:
            type_map[n] = "paper"
        else:
            type_map[n] = "scissors"
    return type_map


def _ensure_state(request) -> dict:
    """
    Ensure a session-backed game state exists for the current match.
    Also migrates older/bad states (no type_map, wrong key types, etc).
    """
    state = request.session.get("card_game")

    def fresh_state():
        tm = _new_type_map()
        return {
            "player_wins": 0,
            "bot_wins": 0,
            "round": 1,
            "history": [],
            "player_remaining": sorted(tm.keys()),
            "bot_remaining": sorted(tm.keys()),
            "type_map": tm,
        }

    # No state yet → create fresh
    if not isinstance(state, dict):
        state = fresh_state()
        request.session["card_game"] = state
        return state

    changed = False

    # Validate type_map
    tm = state.get("type_map")
    if not isinstance(tm, dict) or len(tm) != 9:
        state = fresh_state()
        request.session["card_game"] = state
        return state

    # --- Normalize keys to ints (fix for '5' vs 5) ---
    try:
        tm_int = {int(k): v for k, v in tm.items()}
    except Exception:
        state = fresh_state()
        request.session["card_game"] = state
        return state

    # Ensure values are only valid types
    valid_types = {"rock", "paper", "scissors"}
    if any(v not in valid_types for v in tm_int.values()):
        state = fresh_state()
        request.session["card_game"] = state
        return state

    # Write back normalized map if changed
    if tm_int != tm:
        state["type_map"] = tm_int
        changed = True
    tm = tm_int

    # Normalize remaining lists to ints and keep only keys present in tm
    def norm_remaining(lst):
        if not isinstance(lst, list):
            return sorted(tm.keys())
        acc = []
        for x in lst:
            try:
                xi = int(x)
                if xi in tm:
                    acc.append(xi)
            except Exception:
                pass
        # if empty after normalization, repopulate with all keys
        return sorted(acc) if acc else sorted(tm.keys())

    pr = norm_remaining(state.get("player_remaining"))
    br = norm_remaining(state.get("bot_remaining"))
    if pr != state.get("player_remaining"):
        state["player_remaining"] = pr
        changed = True
    if br != state.get("bot_remaining"):
        state["bot_remaining"] = br
        changed = True

    # Backfill counters
    if not isinstance(state.get("player_wins"), int):
        state["player_wins"] = 0; changed = True
    if not isinstance(state.get("bot_wins"), int):
        state["bot_wins"] = 0; changed = True
    if not isinstance(state.get("round"), int) or state["round"] < 1:
        state["round"] = 1; changed = True
    if not isinstance(state.get("history"), list):
        state["history"] = []; changed = True

    if changed:
        request.session["card_game"] = state
        request.session.modified = True

    return state

def _reset_state(request):
    if "card_game" in request.session:
        del request.session["card_game"]


def card_type(card_num: int, type_map: dict) -> str:
    # Be tolerant of int/str keys in the session
    if card_num in type_map:
        return type_map[card_num]
    if str(card_num) in type_map:
        return type_map[str(card_num)]
    if int(card_num) in type_map:
        return type_map[int(card_num)]
    # Fallback (shouldn't happen after normalization)
    raise KeyError(f"card {card_num} not in type_map")


def decide_winner(
    player_card: int, bot_card: int, type_map: Dict[int, str]
) -> Tuple[str, str]:
    """
    Returns (outcome, reason)
    outcome ∈ {'player', 'bot', 'tie'}
    """
    pt = card_type(player_card, type_map)
    bt = card_type(bot_card, type_map)

    if pt != bt:
        if BEATS[pt] == bt:
            return "player", f"{pt.capitalize()} beats {bt}."
        else:
            return "bot", f"{bt.capitalize()} beats {pt}."
    else:
        if player_card > bot_card:
            return "player", f"Both {pt}; {player_card} > {bot_card}."
        elif bot_card > player_card:
            return "bot", f"Both {pt}; {bot_card} > {player_card}."
        else:
            return "tie", f"Both {pt}; both {player_card}."


# ----- View -----
def card_game(request):
    """
    One match of best-of-three (first to 2).
    - Types (rock/paper/scissors) override numbers.
    - If same type, higher number wins.
    - Each card number can only be used once per side during the match.
    - Numbers 1..9 are randomly assigned to types per match.
    """
    # Reset match if requested
    if request.GET.get("reset"):
        _reset_state(request)
        # If your URLs are namespaced, change to redirect("exo:card_game")
        return redirect("card_game")

    state = _ensure_state(request)
    type_map: Dict[int, str] = state["type_map"]

    picked = request.GET.get("card")
    player_card: Optional[int] = None
    bot_card: Optional[int] = None
    result = None
    reason = None
    banner = None

    finished = state["player_wins"] >= WIN_TARGET or state["bot_wins"] >= WIN_TARGET

    # Defensive end if somehow out of cards
    if not finished and (not state["player_remaining"] or not state["bot_remaining"]):
        finished = True

    if picked and not finished:
        try:
            player_card = int(picked)
        except ValueError:
            player_card = None

        # Validate player pick is still available
        if player_card not in state["player_remaining"]:
            banner = "You already used that card. Pick another."
            player_card = None
        else:
            # Bot chooses only from its remaining cards
            bot_card = random.choice(state["bot_remaining"])

            outcome, reason = decide_winner(player_card, bot_card, type_map)

            # Record round
            state["history"].append({
                "round": state["round"],
                "player_card": player_card,
                "player_type": card_type(player_card, type_map),
                "bot_card": bot_card,
                "bot_type": card_type(bot_card, type_map),
                "outcome": outcome,
                "reason": reason,
            })

            # Remove used cards
            state["player_remaining"].remove(player_card)
            state["bot_remaining"].remove(bot_card)

            # Score
            if outcome == "player":
                state["player_wins"] += 1
                result = "Player wins the round!"
            elif outcome == "bot":
                state["bot_wins"] += 1
                result = "Bot wins the round!"
            else:
                result = "Round is a tie."

            # Advance round and possibly finish
            state["round"] += 1
            finished = state["player_wins"] >= WIN_TARGET or state["bot_wins"] >= WIN_TARGET

            # Persist
            request.session["card_game"] = state
            request.session.modified = True

    # Match winner text
    match_winner = None
    if finished:
        if state["player_wins"] > state["bot_wins"]:
            match_winner = "Player"
        elif state["bot_wins"] > state["player_wins"]:
            match_winner = "Bot"
        else:
            match_winner = "Tie"

    return render(request, "exo/card_game.html", {
        "cards": sorted(type_map.keys()),
        "type_map": type_map,
        "player_card": player_card,
        "player_type": card_type(player_card, type_map) if player_card else None,
        "bot_card": bot_card,
        "bot_type": card_type(bot_card, type_map) if bot_card else None,
        "result": result,
        "reason": reason,
        "score_player": state["player_wins"],
        "score_bot": state["bot_wins"],
        "round_num": state["round"],
        "history": state["history"],
        "finished": finished,
        "match_winner": match_winner,
        "player_remaining": state["player_remaining"],
        "bot_remaining": state["bot_remaining"],
        "banner": banner,
    })