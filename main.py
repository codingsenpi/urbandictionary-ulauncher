import json
import requests
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction


class UrbanDictionaryExtension(Extension):

    def __init__(self):
        super(UrbanDictionaryExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []
        query = event.get_argument()

        if not query:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='Enter a word to search',
                    on_enter=HideWindowAction()
                )
            ])

        try:
            response = requests.get('https://api.urbandictionary.com/v0/define?term=%s' % query)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()

            if not data or not data['list']:
                return RenderResultListAction([
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name='No results found for "%s"' % query,
                        on_enter=HideWindowAction()
                    )
                ])

            for result in data['list']:
                items.append(
                    ExtensionResultItem(
                        icon='images/icon.png',
                        name=result['word'],
                        description=result['definition'],
                        on_enter=CopyToClipboardAction(result['definition'])
                    )
                )

            return RenderResultListAction(items)

        except requests.exceptions.RequestException as e:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='Error fetching definitions',
                    description=str(e),
                    on_enter=HideWindowAction()
                )
            ])
        except (ValueError, KeyError) as e:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='Error parsing response',
                    description=str(e),
                    on_enter=HideWindowAction()
                )
            ])


if __name__ == '__main__':
    UrbanDictionaryExtension().run()
