from django import test

from . import models, forms

NO_ACTIVE_ROOMS_TEXT = "No active rooms right now"
MAKE_ROOM_BUTTON = '<input type="submit" class="form-control" value="Make Room" />'
JOIN_ROOM_BUTTON = '<input type="submit" class="form-control" value="Join Room" />'
BOARD_CONTAINER_HTML = '<div class="board-container">'

class HomeTestCase(test.TestCase):

    def setUp(self):
        self.room_form = forms.RoomForm({
            "room_name": "Test Room",
            "passphrase": "password",
            "nickname": "Bingoer",
            "game_type": str(models.GameType.ocarina_of_time.value),
            "lockout_mode": str(models.LockoutMode.lockout.value),
        })

    def test_home_empty(self):
        resp = self.client.get("/")
        self.assertContains(resp, NO_ACTIVE_ROOMS_TEXT)
        self.assertNotContains(resp, "<tr>", html=True)
        self.assertContains(resp, MAKE_ROOM_BUTTON, html=True)

    def test_home_create_room(self):
        self.assertTrue(self.room_form.is_valid())
        # test room creation
        create_resp = self.client.post("/", self.room_form.data, follow=True)
        self.assertContains(create_resp, "Test Room")
        self.assertContains(create_resp, BOARD_CONTAINER_HTML)
        self.assertNotContains(create_resp, JOIN_ROOM_BUTTON)

        room_url = create_resp.context["room"].get_absolute_url()

        # test that the creator is redirected properly
        creator_resp = self.client.get(room_url)
        self.assertContains(creator_resp, "Test Room")
        self.assertContains(creator_resp, BOARD_CONTAINER_HTML)
        self.assertNotContains(creator_resp, JOIN_ROOM_BUTTON)

        # test that a new user gets the join screen
        new_resp = test.Client().get(room_url)
        self.assertContains(new_resp, "Test Room")
        self.assertNotContains(new_resp, BOARD_CONTAINER_HTML)
        self.assertContains(new_resp, JOIN_ROOM_BUTTON, html=True)

    def test_home_one_room(self):
        # test home page when one room already exists
        if not self.room_form.is_valid():
            self.fail("form error: " + repr(self.room_form.errors))
        room = self.room_form.create_room()
        resp = self.client.get("/")
        self.assertNotContains(resp, "No active rooms right now")
        room_td = '<td><a href="' + room.get_absolute_url() + '">Test Room</a></td>'
        self.assertContains(resp, room_td)
        self.assertContains(resp, MAKE_ROOM_BUTTON, html=True)

