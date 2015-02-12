from django.shortcuts import render
from corehq import toggles
from corehq.apps.domain.decorators import login_and_domain_required
from corehq.apps.feedback.forms import FeedbackForm


@toggles.SMS_FEEDBACK.required_decorator()
@login_and_domain_required
def feedback_home(request, domain):
    form = FeedbackForm()
    return render(request, 'feedback/configure_feedback.html', {
        'domain': domain,
        'form': form,
    })
