import React, { useState, useEffect } from 'react';
import {
    UserCircleIcon,
    ChartBarIcon,
    BellIcon,
    ComputerDesktopIcon,
    EyeIcon,
    ShieldCheckIcon,
    CreditCardIcon,
    ClockIcon
} from '@heroicons/react/24/outline';
import {
    useGetProfileBasicQuery,
    useUpdateProfileBasicMutation,
    useGetNotificationSettingsQuery,
    useUpdateNotificationSettingsMutation,
    useGetDisplayPreferencesQuery,
    useUpdateDisplayPreferencesMutation,
    useGetUserActivityQuery,
    useGetLoginHistoryQuery,
    useGetSubscriptionQuery
} from '../services/api';
import { toast } from 'react-hot-toast';

// --- Basic Info Tab ---
const BasicInfoTab = () => {
    const { data: profile, isLoading } = useGetProfileBasicQuery();
    const [updateProfile, { isLoading: isUpdating }] = useUpdateProfileBasicMutation();
    const [formData, setFormData] = useState({
        full_name: '',
        phone_number: '',
        bio: '',
        address: '',
        city: '',
        country: ''
    });

    useEffect(() => {
        if (profile) {
            setFormData({
                full_name: profile.full_name || '',
                phone_number: profile.phone_number || '',
                bio: profile.bio || '',
                address: profile.address || '',
                city: profile.city || '',
                country: profile.country || ''
            });
        }
    }, [profile]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await updateProfile(formData).unwrap();
            toast.success('Profile updated successfully');
        } catch (error) {
            toast.error('Failed to update profile');
        }
    };

    if (isLoading) return <div className="p-6">Loading...</div>;

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Basic Information</h3>
            <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                    <div className="sm:col-span-3">
                        <label htmlFor="profile-full-name" className="block text-sm font-medium text-gray-700">Full Name</label>
                        <input
                            id="profile-full-name"
                            name="full_name"
                            type="text"
                            autoComplete="name"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            value={formData.full_name}
                            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                        />
                    </div>
                    <div className="sm:col-span-3">
                        <label htmlFor="profile-phone" className="block text-sm font-medium text-gray-700">Phone Number</label>
                        <input
                            id="profile-phone"
                            name="phone_number"
                            type="tel"
                            autoComplete="tel"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            value={formData.phone_number}
                            onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                        />
                    </div>
                    <div className="sm:col-span-6">
                        <label htmlFor="profile-bio" className="block text-sm font-medium text-gray-700">Bio</label>
                        <textarea
                            id="profile-bio"
                            name="bio"
                            rows={3}
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            value={formData.bio}
                            onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                        />
                    </div>
                    <div className="sm:col-span-6">
                        <label htmlFor="profile-address" className="block text-sm font-medium text-gray-700">Address</label>
                        <input
                            id="profile-address"
                            name="address"
                            type="text"
                            autoComplete="street-address"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            value={formData.address}
                            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                        />
                    </div>
                    <div className="sm:col-span-3">
                        <label htmlFor="profile-city" className="block text-sm font-medium text-gray-700">City</label>
                        <input
                            id="profile-city"
                            name="city"
                            type="text"
                            autoComplete="address-level2"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            value={formData.city}
                            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                        />
                    </div>
                    <div className="sm:col-span-3">
                        <label htmlFor="profile-country" className="block text-sm font-medium text-gray-700">Country</label>
                        <input
                            id="profile-country"
                            name="country"
                            type="text"
                            autoComplete="country-name"
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                            value={formData.country}
                            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                        />
                    </div>
                </div>
                <div className="mt-6 flex justify-end">
                    <button
                        type="submit"
                        disabled={isUpdating}
                        className="bg-blue-600 border border-transparent rounded-md shadow-sm py-2 px-4 inline-flex justify-center text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                    >
                        {isUpdating ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </form>
        </div>
    );
};

// --- Notification Settings Tab ---
const NotificationSettingsTab = () => {
    const { data: settings, isLoading } = useGetNotificationSettingsQuery();
    const [updateSettings, { isLoading: isUpdating }] = useUpdateNotificationSettingsMutation();
    const [formData, setFormData] = useState({
        email_alerts: true,
        push_notifications: true,
        market_updates: true,
        portfolio_alerts: true,
        security_alerts: true,
        promotional_emails: false
    });

    useEffect(() => {
        if (settings) {
            setFormData({
                email_alerts: settings.email_alerts ?? true,
                push_notifications: settings.push_notifications ?? true,
                market_updates: settings.market_updates ?? true,
                portfolio_alerts: settings.portfolio_alerts ?? true,
                security_alerts: settings.security_alerts ?? true,
                promotional_emails: settings.promotional_emails ?? false
            });
        }
    }, [settings]);

    const handleToggle = async (key: string) => {
        const newData = { ...formData, [key]: !formData[key as keyof typeof formData] };
        setFormData(newData);
        try {
            await updateSettings(newData).unwrap();
            toast.success('Settings updated');
        } catch (error) {
            toast.error('Failed to update settings');
            // Revert on error
            setFormData(formData);
        }
    };

    if (isLoading) return <div className="p-6">Loading...</div>;

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Notification Preferences</h3>
            <div className="space-y-6">
                {Object.entries(formData).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                        <span className="flex-grow flex flex-col">
                            <span className="text-sm font-medium text-gray-900 capitalize">{key.replace(/_/g, ' ')}</span>
                            <span className="text-sm text-gray-500">Receive notifications for {key.replace(/_/g, ' ')}.</span>
                        </span>
                        <button
                            type="button"
                            onClick={() => handleToggle(key)}
                            className={`${value ? 'bg-blue-600' : 'bg-gray-200'
                                } relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                        >
                            <span
                                aria-hidden="true"
                                className={`${value ? 'translate-x-5' : 'translate-x-0'
                                    } pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform ring-0 transition ease-in-out duration-200`}
                            />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

// --- Display Preferences Tab ---
const DisplayPreferencesTab = () => {
    const { data: prefs, isLoading } = useGetDisplayPreferencesQuery();
    const [updatePrefs, { isLoading: isUpdating }] = useUpdateDisplayPreferencesMutation();
    const [formData, setFormData] = useState({
        theme: 'light',
        currency: 'INR',
        language: 'en',
        chart_preference: 'candlestick',
        compact_mode: false
    });

    useEffect(() => {
        if (prefs) {
            setFormData({
                theme: prefs.theme || 'light',
                currency: prefs.currency || 'INR',
                language: prefs.language || 'en',
                chart_preference: prefs.chart_preference || 'candlestick',
                compact_mode: prefs.compact_mode || false
            });
        }
    }, [prefs]);

    const handleChange = async (key: string, value: any) => {
        const newData = { ...formData, [key]: value };
        setFormData(newData);
        try {
            await updatePrefs(newData).unwrap();
            toast.success('Preferences updated');
        } catch (error) {
            toast.error('Failed to update preferences');
        }
    };

    if (isLoading) return <div className="p-6">Loading...</div>;

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Display Settings</h3>
            <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                <div className="sm:col-span-3">
                    <label htmlFor="display-theme" className="block text-sm font-medium text-gray-700">Theme</label>
                    <select
                        id="display-theme"
                        name="theme"
                        value={formData.theme}
                        onChange={(e) => handleChange('theme', e.target.value)}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                    >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="system">System</option>
                    </select>
                </div>
                <div className="sm:col-span-3">
                    <label htmlFor="display-currency" className="block text-sm font-medium text-gray-700">Currency</label>
                    <select
                        id="display-currency"
                        name="currency"
                        value={formData.currency}
                        onChange={(e) => handleChange('currency', e.target.value)}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                    >
                        <option value="INR">INR (₹)</option>
                        <option value="USD">USD ($)</option>
                    </select>
                </div>
                <div className="sm:col-span-3">
                    <label htmlFor="display-chart-preference" className="block text-sm font-medium text-gray-700">Chart Style</label>
                    <select
                        id="display-chart-preference"
                        name="chart_preference"
                        value={formData.chart_preference}
                        onChange={(e) => handleChange('chart_preference', e.target.value)}
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                    >
                        <option value="candlestick">Candlestick</option>
                        <option value="line">Line</option>
                        <option value="area">Area</option>
                    </select>
                </div>
                <div className="sm:col-span-6 flex items-center">
                    <input
                        id="compact_mode"
                        name="compact_mode"
                        type="checkbox"
                        checked={formData.compact_mode}
                        onChange={(e) => handleChange('compact_mode', e.target.checked)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="compact_mode" className="ml-2 block text-sm text-gray-900">
                        Compact Mode (Higher data density)
                    </label>
                </div>
            </div>
        </div>
    );
};

// --- Activity Tab ---
const ActivityTab = () => {
    const { data: activities, isLoading: loadingActivity } = useGetUserActivityQuery(20);
    const { data: loginHistory, isLoading: loadingLogin } = useGetLoginHistoryQuery(10);

    if (loadingActivity || loadingLogin) return <div className="p-6">Loading...</div>;

    return (
        <div className="space-y-6">
            <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Recent Activity</h3>
                <div className="flow-root">
                    <ul className="-mb-8">
                        {activities && activities.length > 0 ? (
                            activities.map((activity: any, activityIdx: number) => (
                                <li key={activity.id}>
                                    <div className="relative pb-8">
                                        {activityIdx !== activities.length - 1 ? (
                                            <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                                        ) : null}
                                        <div className="relative flex space-x-3">
                                            <div>
                                                <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                                                    <ClockIcon className="h-5 w-5 text-white" aria-hidden="true" />
                                                </span>
                                            </div>
                                            <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                                                <div>
                                                    <p className="text-sm text-gray-500">
                                                        {activity.activity_type} <span className="font-medium text-gray-900">{activity.details}</span>
                                                    </p>
                                                </div>
                                                <div className="text-right text-sm whitespace-nowrap text-gray-500">
                                                    <time dateTime={activity.created_at}>{new Date(activity.created_at).toLocaleDateString()}</time>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            ))
                        ) : (
                            <p className="text-gray-500">No recent activity.</p>
                        )}
                    </ul>
                </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Login History</h3>
                <div className="flex flex-col">
                    <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                        <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Date & Time
                                            </th>
                                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                IP Address
                                            </th>
                                            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Device
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {loginHistory && loginHistory.map((login: any) => (
                                            <tr key={login.id}>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    {new Date(login.login_time).toLocaleString()}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    {login.ip_address}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    {login.device_info}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// --- Subscription Tab ---
const SubscriptionTab = () => {
    const { data: sub, isLoading } = useGetSubscriptionQuery();

    if (isLoading) return <div className="p-6">Loading...</div>;

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Subscription Plan</h3>
            <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
                <dl className="sm:divide-y sm:divide-gray-200">
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                        <dt className="text-sm font-medium text-gray-500">Current Plan</dt>
                        <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 capitalize">{sub?.plan_name || 'Free'}</dd>
                    </div>
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                        <dt className="text-sm font-medium text-gray-500">Status</dt>
                        <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${sub?.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                                {sub?.status || 'Active'}
                            </span>
                        </dd>
                    </div>
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                        <dt className="text-sm font-medium text-gray-500">Price</dt>
                        <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">₹{sub?.price || 0} / month</dd>
                    </div>
                    <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                        <dt className="text-sm font-medium text-gray-500">Next Billing Date</dt>
                        <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                            {sub?.next_billing_date ? new Date(sub.next_billing_date).toLocaleDateString() : 'N/A'}
                        </dd>
                    </div>
                </dl>
            </div>
            <div className="mt-6">
                <button type="button" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                    Upgrade Plan
                </button>
            </div>
        </div>
    );
};

// --- Placeholders for remaining tabs ---
const InvestmentPreferencesTab = () => (
    <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Investment Preferences</h3>
        <p className="text-gray-500">Customize your investment profile and goals. (Coming Soon)</p>
    </div>
);

const WatchlistPortfolioTab = () => (
    <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Watchlist & Portfolio</h3>
        <p className="text-gray-500">Manage your watchlists and portfolio settings. (Coming Soon)</p>
    </div>
);

const SecurityTab = () => (
    <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Security</h3>
        <p className="text-gray-500">Update password and security settings. (Coming Soon)</p>
    </div>
);

const Profile: React.FC = () => {
    const [activeTab, setActiveTab] = useState('basic');

    const tabs = [
        { id: 'basic', name: 'Basic Info', icon: UserCircleIcon, component: BasicInfoTab },
        { id: 'investment', name: 'Investment', icon: ChartBarIcon, component: InvestmentPreferencesTab },
        { id: 'notifications', name: 'Notifications', icon: BellIcon, component: NotificationSettingsTab },
        { id: 'display', name: 'Display', icon: ComputerDesktopIcon, component: DisplayPreferencesTab },
        { id: 'watchlist', name: 'Watchlist', icon: EyeIcon, component: WatchlistPortfolioTab },
        { id: 'security', name: 'Security', icon: ShieldCheckIcon, component: SecurityTab },
        { id: 'subscription', name: 'Subscription', icon: CreditCardIcon, component: SubscriptionTab },
        { id: 'activity', name: 'Activity', icon: ClockIcon, component: ActivityTab },
    ];

    const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || BasicInfoTab;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="md:flex md:items-center md:justify-between mb-8">
                <div className="flex-1 min-w-0">
                    <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
                        Account Settings
                    </h2>
                    <p className="mt-1 text-sm text-gray-500">
                        Manage your profile, preferences, and account security.
                    </p>
                </div>
            </div>

            <div className="lg:grid lg:grid-cols-12 lg:gap-x-5">
                <aside className="py-6 px-2 sm:px-6 lg:py-0 lg:px-0 lg:col-span-3">
                    <nav className="space-y-1">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`
                  group rounded-md px-3 py-2 flex items-center text-sm font-medium w-full
                  ${activeTab === tab.id
                                        ? 'bg-gray-50 text-blue-700 hover:text-blue-700 hover:bg-white'
                                        : 'text-gray-900 hover:text-gray-900 hover:bg-gray-50'
                                    }
                `}
                            >
                                <tab.icon
                                    className={`
                    flex-shrink-0 -ml-1 mr-3 h-6 w-6
                    ${activeTab === tab.id ? 'text-blue-700' : 'text-gray-400 group-hover:text-gray-500'}
                  `}
                                    aria-hidden="true"
                                />
                                <span className="truncate">{tab.name}</span>
                            </button>
                        ))}
                    </nav>
                </aside>

                <div className="space-y-6 sm:px-6 lg:px-0 lg:col-span-9">
                    <ActiveComponent />
                </div>
            </div>
        </div>
    );
};

export default Profile;
