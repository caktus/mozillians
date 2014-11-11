from json import loads

from django.conf import settings

from mock import patch, Mock
from mozillians.common.tests import TestCase
from mozillians.common.authbackend import BrowserIDVerify, MozilliansAuthBackend
from mozillians.users.models import ExternalAccount
from mozillians.users.tests import UserFactory
from nose.tools import eq_, ok_


class BrowserIDVerifyTests(TestCase):
    @patch('mozillians.common.authbackend.Verify.post')
    def test_post_anonymous(self, verify_post_mock):
        Verify = BrowserIDVerify()
        request_mock = Mock()
        request_mock.user.is_authenticated.return_value = False
        Verify.request = request_mock
        Verify.post()
        verify_post_mock.assert_called_with()

    @patch('mozillians.common.authbackend.get_audience')
    @patch('mozillians.common.authbackend.RemoteVerifier.verify')
    def test_post_authenticated(self, verify_mock, get_audience_mock):
        user = UserFactory.create()
        Verify = BrowserIDVerify()
        request_mock = Mock()
        request_mock.user.is_authenticated.return_value = True
        request_mock.user = user
        request_mock.POST = {'assertion': 'assertion'}
        Verify.request = request_mock
        get_audience_mock.return_value = 'audience'
        verify_mock.return_value = Mock(email='foo@example.com')
        Verify.post()
        verify_mock.assert_called_with('assertion', 'audience')
        get_audience_mock.assert_called_with(request_mock)
        emails = ExternalAccount.objects.filter(type=ExternalAccount.TYPE_EMAIL,
                                                identifier='foo@example.com',
                                                user=user.userprofile)
        ok_(emails.exists())

    @patch('mozillians.common.authbackend.BrowserIDVerify.login_failure')
    @patch('mozillians.common.authbackend.get_audience')
    @patch('mozillians.common.authbackend.RemoteVerifier.verify')
    def test_post_valid_email_exists(self, verify_mock, get_audience_mock,
                                     login_failure_mock):
        UserFactory.create(email='foo@example.com')
        user = UserFactory.create(email='la@example.com')
        Verify = BrowserIDVerify()
        request_mock = Mock()
        request_mock.user.is_authenticated.return_value = True
        request_mock.user = user
        request_mock.POST = {'assertion': 'assertion'}
        Verify.request = request_mock
        verify_mock.return_value = Mock(email='foo@example.com')
        get_audience_mock.return_value = 'audience'
        Verify.post()
        verify_mock.assert_called_with('assertion', 'audience')
        get_audience_mock.assert_called_with(request_mock)
        login_failure_mock.assert_called_with()
        ok_(Verify.add_email)

    @patch('mozillians.common.authbackend.BrowserIDVerify.login_success')
    @patch('mozillians.common.authbackend.get_audience')
    @patch('mozillians.common.authbackend.RemoteVerifier.verify')
    def test_post_add_email(self, verify_mock, get_audience_mock,
                            login_success_mock):
        user = UserFactory.create(email='la@example.com')
        Verify = BrowserIDVerify()
        request_mock = Mock()
        request_mock.user.is_authenticated.return_value = True
        request_mock.user = user
        request_mock.POST = {'assertion': 'assertion'}
        Verify.request = request_mock
        verify_mock.return_value = Mock(email='foo@example.com')
        get_audience_mock.return_value = 'audience'
        Verify.post()
        verify_mock.assert_called_with('assertion', 'audience')
        get_audience_mock.assert_called_with(request_mock)
        login_success_mock.assert_called_with()

        emails = ExternalAccount.objects.filter(type=ExternalAccount.TYPE_EMAIL,
                                                identifier='foo@example.com',
                                                user=user.userprofile)
        ok_(emails.exists())
        ok_(Verify.add_email)

    def test_failure_url_add_email(self):
        Verify = BrowserIDVerify()
        Verify.add_email = True
        user = UserFactory.create(email='la@example.com')
        request_mock = Mock()
        request_mock.user.is_authenticated.return_value = True
        request_mock.user = user
        url = Verify.failure_url
        eq_(url, '/user/edit/emails/')

    def test_login_success_add_email(self):
        Verify = BrowserIDVerify()
        Verify.add_email = True
        user = UserFactory.create(email='la@example.com')
        request_mock = Mock()
        request_mock.user.is_authenticated.return_value = True
        request_mock.user = user
        Verify.user = user
        response = loads(Verify.login_success().content)
        eq_(response['redirect'], '/user/edit/emails/')


class ReferralSourceTests(TestCase):

    @patch('mozillians.common.authbackend.BrowserIDBackend.authenticate')
    def test_get_involved_source(self, authenticate_mock):
        Authenticate = MozilliansAuthBackend()
        request_mock = Mock()
        request_mock.META = {'HTTP_REFERER': settings.SITE_URL + '/?source=contribute'}
        Authenticate.request = request_mock
        Authenticate.authenticate(request=request_mock)
        eq_(Authenticate.referral_source, 'contribute')

    @patch('mozillians.common.authbackend.BrowserIDBackend.authenticate')
    def test_random_source(self, authenticate_mock):
        Authenticate = MozilliansAuthBackend()
        request_mock = Mock()
        request_mock.META = {'HTTP_REFERER': settings.SITE_URL + '/?source=foobar'}
        Authenticate.request = request_mock
        Authenticate.authenticate(request=request_mock)
        eq_(Authenticate.referral_source, None)
