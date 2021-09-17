from django import forms


class EnterRoomForm(forms.Form):
    username = forms.CharField(max_length=50, label='Ник-нейм')
