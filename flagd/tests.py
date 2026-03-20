from django.test import TestCase

# Create your tests here.
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
import json

from flagd.models import UserProfile, Flag, CountryAlias
from flagd.forms import UserForm, DeleteAccountForm


# this is the base test class used by other test classes
# basically creates some test data (2 users and 3 flags)
class BaseFlagDTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser1",
            email="testuser1@example.com",
            password="testpass123"
        )
        self.profile = UserProfile.objects.create(user=self.user, score=50)

        self.other_user = User.objects.create_user(
            username="testuser2",
            email="testuser2@example.com",
            password="testpass123"
        )
        self.other_profile = UserProfile.objects.create(user=self.other_user, score=100)

        self.flag1 = Flag.objects.create(
            country_name="Ukraine",
            country_code="ua",
            continent="europe"
        )
        self.flag2 = Flag.objects.create(
            country_name="Japan",
            country_code="jp",
            continent="asia"
        )
        self.flag3 = Flag.objects.create(
            country_name="Australia",
            country_code="au",
            continent="oceania"
        )

        self.alias1 = CountryAlias.objects.create(
            flag=self.flag1,
            alias_name="UA"
        )
        self.alias2 = CountryAlias.objects.create(
            flag=self.flag2,
            alias_name="Nippon"
        )


# this tests model behaviour works as intended
class ModelTests(BaseFlagDTestCase):
    # does converting a user to __str__ give username
    def test_userprofile_str(self):
        self.assertEqual(str(self.profile), "testuser1")

    # converting a flag to string gives country name?
    def test_flag_str(self):
        self.assertEqual(str(self.flag1), "Ukraine")

    # does alias work?
    def test_country_alias_str(self):
        self.assertEqual(str(self.alias2), "Japan → Nippon")


# checks for if valid or invalid inputs are handled correctly in forms
class FormTests(BaseFlagDTestCase):
    # valid user data form check
    def test_user_form_valid(self):
        form = UserForm(data={
            "username": "valid_name-123",
            "email": "new@example.com",
            "password1": "ComplexPass123",
            "password2": "ComplexPass123",
        })
        self.assertTrue(form.is_valid())

    # invalid - spaces/punctuation check
    def test_user_form_rejects_invalid_username(self):
        form = UserForm(data={
            "username": "bad username!",
            "email": "new@example.com",
            "password1": "ComplexPass123",
            "password2": "ComplexPass123",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    # correct username and password, pass
    def test_delete_account_form_valid(self):
        form = DeleteAccountForm(self.user, data={
            "password": "testpass123",
            "confirm_text": "DELETE",
        })
        self.assertTrue(form.is_valid())

    # incorrect text, fails
    def test_delete_account_form_rejects_wrong_confirm_text(self):
        form = DeleteAccountForm(self.user, data={
            "password": "testpass123",
            "confirm_text": "delete",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_text", form.errors)

    # user can delete account?
    def test_delete_account_form_rejects_wrong_password(self):
        form = DeleteAccountForm(self.user, data={
            "password": "wrongpass",
            "confirm_text": "DELETE",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)


# Tests for pages which are public are accessible/viewable without being signed in
class PublicViewTests(BaseFlagDTestCase):
    # index page check
    def test_index_page_loads(self):
        response = self.client.get(reverse("flagd:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/index.html")
        self.assertContains(response, "Welcome to FLAGD!")

    # index page also loads leaderboard correctly?
    def test_index_orders_top_users_by_score(self):
        response = self.client.get(reverse("flagd:index"))
        top_users = list(response.context["top_users"])
        self.assertEqual(top_users[0].username, "testuser2")
        self.assertEqual(top_users[1].username, "testuser1")

    def test_about_page_loads(self):
        response = self.client.get(reverse("flagd:about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/about.html")

    # Leaderboard page laods correctly?
    def test_leaderboard_page_loads(self):
        response = self.client.get(reverse("flagd:leaderboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/leaderboard.html")

    # Also users on leaderboard ordered correctly by score? (Highest fiurst)
    def test_leaderboard_orders_users_by_score(self):
        response = self.client.get(reverse("flagd:leaderboard"))
        users = list(response.context["users"])
        self.assertEqual(users[0].username, "testuser2")
        self.assertEqual(users[1].username, "testuser1")

    # Account page loads correctly
    def test_account_page_loads(self):
        response = self.client.get(reverse("flagd:account"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/account.html")

    def test_play_redirects_unauthenticated_user_without_guest_mode(self):
        response = self.client.get(reverse("flagd:play"))
        self.assertRedirects(response, reverse("flagd:account"))

    # check if the continue as guest functionality works correctly,
    def test_continue_as_guest_sets_session_and_redirects(self):
        response = self.client.get(reverse("flagd:continue_as_guest"))
        self.assertRedirects(response, reverse("flagd:play"))
        session = self.client.session
        self.assertTrue(session.get("guest_mode"))

    # continue as guest redirects to play page?
    def test_play_loads_for_guest_mode(self):
        session = self.client.session
        session["guest_mode"] = True
        session.save()

        response = self.client.get(reverse("flagd:play"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/play.html")
    
    def test_catalogue_page_loads(self):
        response = self.client.get(reverse("flagd:catalogue"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/catalogue.html")


# non public views tests/authenticated view tests (like profile)
class AuthenticationViewTests(BaseFlagDTestCase):
    # valid login redirects to user login page?
    def test_account_post_logs_user_in_and_redirects(self):
        response = self.client.post(reverse("flagd:account"), {
            "username": "testuser1",
            "password": "testpass123",
        })
        self.assertRedirects(
            response,
            reverse("flagd:user_profile", kwargs={"profile_name_slug": "testuser1"})
        )
    
    # check wrong password fails
    def test_account_post_invalid_login_shows_error(self):
        response = self.client.post(reverse("flagd:account"), {
            "username": "testuser1",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    #check sign up creates correct user and userprofile objects
    @override_settings(DEFAULT_PFPS=["profile_pics/default.png"])
    def test_sign_up_creates_user_and_profile(self):
        response = self.client.post(reverse("flagd:sign_up"), {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "ComplexPass123",
            "password2": "ComplexPass123",
        })
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(UserProfile.objects.filter(user__username="newuser").exists())
        self.assertRedirects(
            response,
            reverse("flagd:user_profile", kwargs={"profile_name_slug": "newuser"})
        )

    # if not logged in gets redirected?
    def test_user_profile_requires_login(self):
        response = self.client.get(
            reverse("flagd:user_profile", kwargs={"profile_name_slug": "testuster1"})
        )
        self.assertEqual(response.status_code, 302)

    # logged in can view preofile page
    def test_user_profile_loads_when_logged_in(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(
            reverse("flagd:user_profile", kwargs={"profile_name_slug": "testuser1"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/user_profile.html")

    # settings page works logged in?
    def test_user_settings_requires_login(self):
        response = self.client.get(reverse("flagd:user_settings"))
        self.assertEqual(response.status_code, 302)

    # logout redirect if not logged in?
    def test_logout_requires_login(self):
        response = self.client.get(reverse("flagd:logout"))
        self.assertEqual(response.status_code, 302)

    # if logged in and log out, redirected to homepoage successfully?
    def test_logout_when_logged_in_redirects_to_index(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(reverse("flagd:logout"))
        self.assertRedirects(response, reverse("flagd:index"))


# Tests for the catalogue pages , load check not done as was done earlier 
class CatalogueAndFlagTests(BaseFlagDTestCase):
    #search by coutnry name redirects correctly?
    def test_catalogue_search_by_country_name(self):
        response = self.client.get(reverse("flagd:catalogue"), {"q": "Ukraine"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("flagd:flag_detail", kwargs={"flag_id": self.flag1.flag_id})
        )
    
    # searching by alias also redirects correct;y?
    def test_catalogue_search_by_alias_redirects_to_exact_match(self):
        response = self.client.get(reverse("flagd:catalogue"), {"q": "Nippon"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("flagd:flag_detail", kwargs={"flag_id": self.flag2.flag_id})
        )
    
    # flag country page/ extra detials page loads correctly?
    def test_flag_detail_page_loads(self):
        response = self.client.get(
            reverse("flagd:flag_detail", kwargs={"flag_id": self.flag1.flag_id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/flag_detail.html")
        self.assertContains(response, "Ukraine")


#  Testing if the main gameplay flow works as intended
class PlayFlowTests(BaseFlagDTestCase):
    #use guest mode for these tests 
    def setUp(self):
        super().setUp()
        session = self.client.session
        session["guest_mode"] = True
        session.save()

    # timer selection page lods?
    def test_play_timer_loads(self):
        response = self.client.get(
            reverse("flagd:play_timer", kwargs={"mode": "global"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/play_timer.html")

    # question set up page loads, correctly counts total flags
    def test_play_questions_loads_and_has_total_flags(self):
        response = self.client.get(
            reverse("flagd:play_questions", kwargs={"mode": "global"}),
            {"timer": 20}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/play_questions.html")
        self.assertEqual(response.context["total_flags"], 3)

    # has both asia and oceiania 
    def test_play_questions_asiaoceania_counts_asia_and_oceania(self):
        response = self.client.get(
            reverse("flagd:play_questions", kwargs={"mode": "asiaoceania"}),
            {"timer": 20}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_flags"], 2)

    # Normal page request foer the game returns HTMl page?
    def test_play_game_loads_non_ajax(self):
        response = self.client.get(
            reverse("flagd:play_game", kwargs={"mode": "global"}),
            {"timer": 20, "num_questions": 2, "current_question": 1}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/play_game.html")
        self.assertIn("initial_data_json", response.context)
    
    # AJAX request returns proper JSON format?
    def test_play_game_returns_json_for_ajax(self):
        response = self.client.get(
            reverse("flagd:play_game", kwargs={"mode": "global"}),
            {"timer": 20, "num_questions": 2, "current_question": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("flag", data)
        self.assertIn("mode", data)
        self.assertEqual(data["mode"], "global")

    # Quiz resulkt posts correctly and is stored in session properly?
    def test_save_quiz_result_saves_to_session(self):
        payload = {
            "flag_id": self.flag1.flag_id,
            "country_name": "Ukraine",
            "country_code": "ua",
            "is_correct": True,
            "current_question": 1,
            "score": 900,
            "time_taken": 3,
        }
        response = self.client.post(
            reverse("flagd:save_quiz_result"),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        session = self.client.session
        self.assertIn("quiz_results", session)
        self.assertEqual(len(session["quiz_results"]), 1)
        self.assertEqual(session["quiz_results"][0]["country_name"], "Ukraine")

    def test_play_results_calculates_stats(self):
        session = self.client.session
        session["quiz_results"] = [
            {
                "flag_id": self.flag1.flag_id,
                "country_name": "Ukraine",
                "country_code": "ua",
                "is_correct": True,
                "question_number": 1,
                "score": 800,
                "time_taken": 2,
            },
            {
                "flag_id": self.flag2.flag_id,
                "country_name": "Japan",
                "country_code": "jp",
                "is_correct": False,
                "question_number": 2,
                "score": 0,
                "time_taken": 20,
            },
        ]
        session.save()

        response = self.client.get(
            reverse("flagd:play_results", kwargs={"mode": "global"}),
            {"timer": 30, "num_questions": 2, "total_score": 800}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "flagd/play_results.html")
        self.assertEqual(response.context["correct_answers"], 1)
        self.assertEqual(response.context["incorrect_answers"], 1)
        self.assertEqual(response.context["total_questions"], 2)

    # Score only added to user's score field if appropriate game modes selected (not region for example)
    def test_play_results_updates_score_for_high_score_game_only(self):
        self.client.login(username="testuser1", password="testpass123")

        session = self.client.session
        session["quiz_results"] = [
            {
                "flag_id": self.flag1.flag_id,
                "country_name": "Ukraine",
                "country_code": "ua",
                "is_correct": True,
                "question_number": 1,
                "score": 700,
                "time_taken": 4,
            },
            {
                "flag_id": self.flag2.flag_id,
                "country_name": "Japan",
                "country_code": "jp",
                "is_correct": True,
                "question_number": 2,
                "score": 800,
                "time_taken": 4,
            },
        ]
        session.save()

        old_score = self.user.userprofile.score

        response = self.client.get(
            reverse("flagd:play_results", kwargs={"mode": "global"}),
            {"timer": 20, "num_questions": 10, "total_score": 1500}
        )
        self.assertEqual(response.status_code, 200)

        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.score, old_score + 1500)

    # game results don't match score saving rules then don't store the score
    def test_play_results_does_not_update_score_for_non_high_score_game(self):
        self.client.login(username="testuser1", password="testpass123")

        session = self.client.session
        session["quiz_results"] = [
            {
                "flag_id": self.flag1.flag_id,
                "country_name": "Ukraine",
                "country_code": "ua",
                "is_correct": True,
                "question_number": 1,
                "score": 500,
                "time_taken": 5,
            }
        ]
        session.save()

        old_score = self.user.userprofile.score

        response = self.client.get(
            reverse("flagd:play_results", kwargs={"mode": "global"}),
            {"timer": 30, "num_questions": 10, "total_score": 500}
        )
        self.assertEqual(response.status_code, 200)

        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.score, old_score)