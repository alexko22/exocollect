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
        lowest_mass = Planet.objects.order_by('mass')[:5]

        context.update({
            'top_earth_similarity': top_earth_similarity,
            'top_mass': top_mass,
            'top_gravity': top_gravity,
            'lowest_mass': lowest_mass,
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
from typing import Dict, List, Tuple, Optional
from django.shortcuts import render, redirect

# ---------- Game config ----------
COMPOSITIONS = ["carbon", "sulfur", "water"]
COLORS = ["red", "blue", "yellow"]  # stellar/atmospheric variation

# Dominance cycle: carbon > sulfur > water > carbon
BEATS = {"carbon": "sulfur", "sulfur": "water", "water": "carbon"}

HAND_SIZE = 9


# ---------- Helpers ----------
def _new_card(cid: int) -> Dict:
    """Create a brand-new random card with a unique id."""
    return {
        "id": cid,
        "num": random.randint(1, 9),
        "type": random.choice(COMPOSITIONS),
        "color": random.choice(COLORS),
    }


def _new_hand(start_id: int, size: int = HAND_SIZE) -> Tuple[List[Dict], int]:
    """Create a new hand of `size` cards; returns (hand, next_id)."""
    hand = []
    next_id = start_id
    for _ in range(size):
        hand.append(_new_card(next_id))
        next_id += 1
    return hand, next_id


def _find_card_by_id(hand: List[Dict], cid: int) -> Optional[Dict]:
    for c in hand:
        if c["id"] == cid:
            return c
    return None


def _replace_card(hand: List[Dict], cid: int, next_id: int) -> int:
    """Replace the card with id=cid in `hand` with a new card; return new next_id."""
    for i, c in enumerate(hand):
        if c["id"] == cid:
            hand[i] = _new_card(next_id)
            return next_id + 1
    return next_id  # if not found, leave next_id as-is


def decide_winner(player_card: Dict, bot_card: Dict) -> Tuple[str, str]:
    """
    Returns (outcome, reason)
    outcome ∈ {'player', 'bot', 'tie'}
    """
    pt, bt = player_card["type"], bot_card["type"]
    pn, bn = player_card["num"], bot_card["num"]

    if pt != bt:
        if BEATS[pt] == bt:
            return "player", f"{pt.capitalize()} beats {bt}."
        else:
            return "bot", f"{bt.capitalize()} beats {pt}."
    else:
        if pn > bn:
            return "player", f"Both {pt}; {pn} > {bn}."
        elif bn > pn:
            return "bot", f"Both {pt}; {bn} > {pn}."
        else:
            return "tie", f"Both {pt}; both {pn}."


def _fresh_match() -> Dict:
    """Create a brand new match state."""
    next_id = 1
    player_hand, next_id = _new_hand(next_id)
    bot_hand, next_id = _new_hand(next_id)

    return {
        # hands
        "player_hand": player_hand,
        "bot_hand": bot_hand,
        "next_card_id": next_id,

        # progress
        "round": 1,
        "history": [],

        # collections for win condition
        "player_won_colors": [],  # e.g., ["red", "blue"]
        "player_won_types": [],   # e.g., ["rock", "paper"]
        "bot_won_colors": [],
        "bot_won_types": [],

        # finished flag + winner
        "finished": False,
        "winner": None,
    }


def _ensure_state(request) -> Dict:
    """
    Ensure a session-backed game state exists and is well-formed.
    Migrates older states if needed.
    """
    state = request.session.get("card_game_v2")
    changed = False

    def reset():
        s = _fresh_match()
        request.session["card_game_v2"] = s
        return s

    if not isinstance(state, dict):
        return reset()

    # Backfill required keys / types
    must_keys = [
        "player_hand", "bot_hand", "next_card_id", "round", "history",
        "player_won_colors", "player_won_types", "bot_won_colors", "bot_won_types",
        "finished", "winner",
    ]
    for k in must_keys:
        if k not in state:
            state = reset()
            changed = False
            break

    # Basic sanity checks
    if not isinstance(state.get("player_hand"), list) or not isinstance(state.get("bot_hand"), list):
        state = reset()
    if not isinstance(state.get("next_card_id"), int):
        state = reset()
    if not isinstance(state.get("history"), list):
        state["history"] = []
        changed = True
    if not isinstance(state.get("round"), int) or state["round"] < 1:
        state["round"] = 1
        changed = True

    # Ensure hands have the right size; if not, rebuild
    if len(state["player_hand"]) != HAND_SIZE or len(state["bot_hand"]) != HAND_SIZE:
        state = reset()

    if changed:
        request.session["card_game_v2"] = state
        request.session.modified = True

    return state


def _reset_state(request):
    if "card_game_v2" in request.session:
        del request.session["card_game_v2"]


def _add_unique(lst: List[str], value: str):
    if value not in lst:
        lst.append(value)


def _check_win(colors: List[str], types: List[str]) -> bool:
    """Win if you have all three colors OR all three types."""
    return len(set(colors)) == 3 or len(set(types)) == 3


# ---------- View ----------
def card_game(request):
    """
    Card-Jitsu style:
    - Hands of 9 cards per side. Each card: id, num(1..9), type, color.
    - Round outcome: R/P/S overrides number; same type → higher number wins; equal → tie.
    - Win match by collecting (from won rounds) either all 3 colors OR all 3 types.
    - After each round, the used card on each side is replaced by a new random card (hand size stays 9).
    """
    # Reset match?
    if request.GET.get("reset"):
        _reset_state(request)
        return redirect("card_game")  # use 'exo:card_game' if namespaced

    state = _ensure_state(request)

    # If already finished, just render
    if state["finished"]:
        return render(request, "exo/card_game.html", {
            **_template_payload_from_state(state),
            "banner": None,
        })

    # Read player choice (by card id in their hand)
    picked = request.GET.get("card")
    banner = None
    player_card = bot_card = None
    result = reason = None

    if picked:
        try:
            cid = int(picked)
        except ValueError:
            cid = -1

        player_card = _find_card_by_id(state["player_hand"], cid)
        if not player_card:
            banner = "That card is no longer available. Pick another."
        else:
            # Bot chooses a random card from its hand
            bot_card = random.choice(state["bot_hand"])

            outcome, reason = decide_winner(player_card, bot_card)

            # Record round
            state["history"].append({
                "round": state["round"],
                "player": {
                    "num": player_card["num"],
                    "type": player_card["type"],
                    "color": player_card["color"],
                },
                "bot": {
                    "num": bot_card["num"],
                    "type": bot_card["type"],
                    "color": bot_card["color"],
                },
                "outcome": outcome,  # player | bot | tie
                "reason": reason,
            })

            # Tally collections on wins (not ties)
            if outcome == "player":
                _add_unique(state["player_won_colors"], player_card["color"])
                _add_unique(state["player_won_types"], player_card["type"])
                result = "Player wins the round!"
            elif outcome == "bot":
                _add_unique(state["bot_won_colors"], bot_card["color"])
                _add_unique(state["bot_won_types"], bot_card["type"])
                result = "Bot wins the round!"
            else:
                result = "Round is a tie."

            # Replace used cards with new random cards
            next_id = state["next_card_id"]
            next_id = _replace_card(state["player_hand"], player_card["id"], next_id)
            next_id = _replace_card(state["bot_hand"], bot_card["id"], next_id)
            state["next_card_id"] = next_id

            # Check for match win (either set completes)
            if outcome == "player" and _check_win(state["player_won_colors"], state["player_won_types"]):
                state["finished"] = True
                state["winner"] = "Player"
            elif outcome == "bot" and _check_win(state["bot_won_colors"], state["bot_won_types"]):
                state["finished"] = True
                state["winner"] = "Bot"

            # Advance round counter
            state["round"] += 1

            # Persist
            request.session["card_game_v2"] = state
            request.session.modified = True

    # Render
    return render(request, "exo/card_game.html", {
        **_template_payload_from_state(state),
        "banner": banner,
        # last round surface
        "player_last": player_card,
        "bot_last": bot_card,
        "result": result,
        "reason": reason,
    })


# ---------- Template payload ----------
def _template_payload_from_state(state: Dict) -> Dict:
    return {
        "round_num": state["round"],
        "finished": state["finished"],
        "match_winner": state["winner"],

        "player_hand": state["player_hand"],
        "bot_hand": state["bot_hand"],

        "player_won_colors": state["player_won_colors"],
        "player_won_types": state["player_won_types"],
        "bot_won_colors": state["bot_won_colors"],
        "bot_won_types": state["bot_won_types"],

        "history": state["history"],
    }