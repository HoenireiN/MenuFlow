def language(request):

    selected_language = request.session.get('language', 'tr')

    if selected_language not in ('tr', 'en'):
        selected_language = 'tr'

    return {
        'current_language': selected_language,
        'is_turkish': selected_language == 'tr',
    }
