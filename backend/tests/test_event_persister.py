import unittest

from app.services.event_persister import EventPersister


class EventPersisterTests(unittest.TestCase):
    def test_normalize_event_data_maps_standard_type_to_event_type(self):
        event_data = {
            "alert_id": "alert-123",
            "type": "vehicle",
        }

        normalized = EventPersister._normalize_event_data(event_data)

        self.assertEqual(normalized["event_type"], "vehicle")
        self.assertEqual(normalized["type"], "vehicle")

    def test_normalize_event_data_keeps_existing_event_type(self):
        event_data = {
            "alert_id": "alert-123",
            "type": "vehicle",
            "event_type": "intrusion",
        }

        normalized = EventPersister._normalize_event_data(event_data)

        self.assertEqual(normalized["event_type"], "intrusion")


if __name__ == "__main__":
    unittest.main()
