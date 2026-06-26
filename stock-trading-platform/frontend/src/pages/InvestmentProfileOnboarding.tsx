import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useCreateInvestmentProfileMutation } from '../services/api';
import { toast } from 'react-hot-toast';
import {
  BanknotesIcon,
  ChartBarIcon,
  ClockIcon,
  UserIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';

interface FormData {
  investment_amount: number;
  risk_level: 'low' | 'medium' | 'high';
  timeline: 'short' | 'long';
  investment_goals: string;
  monthly_income?: number;
  age?: number;
}

// Props passed to each step component
interface StepProps {
  formData: FormData;
  setFormData: React.Dispatch<React.SetStateAction<FormData>>;
}

// Step 1 – Investment Amount
const Step1: React.FC<StepProps> = React.memo(({ formData, setFormData }) => (
  <motion.div
    initial={{ opacity: 0, x: 50 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -50 }}
    className="space-y-6"
  >
    <div className="text-center">
      <BanknotesIcon className="w-16 h-16 text-blue-600 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        How much do you want to invest?
      </h2>
      <p className="text-gray-600">
        Enter your investment amount in Indian Rupees (₹)
      </p>
    </div>

    <div className="max-w-md mx-auto">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        Investment Amount (₹)
      </label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">₹</span>
        <input
          id="investment-amount"
          name="investment_amount"
          type="number"
          value={formData.investment_amount || ''}
          onChange={e => setFormData({ ...formData, investment_amount: Number(e.target.value) })}
          className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="10,000"
          min="1000"
        />
      </div>
      <div className="mt-4 grid grid-cols-3 gap-2">
        {[10000, 50000, 100000].map(amount => (
          <button
            key={amount}
            onClick={() => setFormData({ ...formData, investment_amount: amount })}
            className="py-2 px-3 border border-gray-300 rounded-lg text-sm hover:bg-gray-50 transition-colors"
          >
            ₹{amount.toLocaleString()}
          </button>
        ))}
      </div>
    </div>
  </motion.div>
));

const colorClasses: Record<string, string> = { green: 'border-green-500 bg-green-50', yellow: 'border-yellow-500 bg-yellow-50', red: 'border-red-500 bg-red-50' };

// Step 2 – Risk Level
const Step2: React.FC<StepProps> = React.memo(({ formData, setFormData }) => (
  <motion.div
    initial={{ opacity: 0, x: 50 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -50 }}
    className="space-y-6"
  >
    <div className="text-center">
      <ChartBarIcon className="w-16 h-16 text-blue-600 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        What's your risk tolerance?
      </h2>
      <p className="text-gray-600">
        This helps us recommend the right stocks for you
      </p>
    </div>

    <div className="max-w-2xl mx-auto space-y-4">
      {[
        {
          value: 'low',
          title: 'Conservative (Low Risk)',
          description: 'I prefer stable returns and want to minimize losses. I like large-cap, dividend-paying stocks.',
          color: 'green'
        },
        {
          value: 'medium',
          title: 'Moderate (Medium Risk)',
          description: 'I want a balance of growth and stability. I can handle some volatility for better returns.',
          color: 'yellow'
        },
        {
          value: 'high',
          title: 'Aggressive (High Risk)',
          description: 'I want maximum growth potential. I can handle high volatility and potential losses.',
          color: 'red'
        }
      ].map(option => (
        <div key={option.value}>
          <label className="cursor-pointer">
            <div
              className={`p-4 border-2 rounded-lg transition-colors ${formData.risk_level === option.value
                ? colorClasses[option.color] || ''
                : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="flex items-start">
                <input
                  type="radio"
                  name="risk_level"
                  value={option.value}
                  checked={formData.risk_level === option.value}
                  onChange={e => setFormData({ ...formData, risk_level: e.target.value as any })}
                  className="mt-1 mr-3"
                />
                <div>
                  <h3 className="font-semibold text-gray-900">{option.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{option.description}</p>
                </div>
              </div>
            </div>
          </label>
        </div>
      ))}
    </div>
  </motion.div>
));

// Step 3 – Timeline
const Step3: React.FC<StepProps> = React.memo(({ formData, setFormData }) => (
  <motion.div
    initial={{ opacity: 0, x: 50 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -50 }}
    className="space-y-6"
  >
    <div className="text-center">
      <ClockIcon className="w-16 h-16 text-blue-600 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        What's your investment timeline?
      </h2>
      <p className="text-gray-600">
        How long do you plan to stay invested?
      </p>
    </div>

    <div className="max-w-xl mx-auto space-y-4">
      {[
        {
          value: 'short',
          title: 'Short-term (1-3 years)',
          description: 'I need my money back relatively soon. Focus on stability and liquidity.',
          icon: '📅'
        },
        {
          value: 'long',
          title: 'Long-term (3+ years)',
          description: 'I can stay invested for the long haul. Focus on growth and wealth creation.',
          icon: '🚀'
        }
      ].map(option => (
        <div key={option.value}>
          <label className="cursor-pointer">
            <div
              className={`p-6 border-2 rounded-lg transition-colors ${formData.timeline === option.value
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'}`}
            >
              <div className="flex items-center">
                <span className="text-2xl mr-4">{option.icon}</span>
                <div className="flex-1">
                  <div className="flex items-center">
                    <input
                      type="radio"
                      name="timeline"
                      value={option.value}
                      checked={formData.timeline === option.value}
                      onChange={e => setFormData({ ...formData, timeline: e.target.value as any })}
                      className="mr-3"
                    />
                    <h3 className="font-semibold text-gray-900">{option.title}</h3>
                  </div>
                  <p className="text-sm text-gray-600 mt-1 ml-6">{option.description}</p>
                </div>
              </div>
            </div>
          </label>
        </div>
      ))}
    </div>
  </motion.div>
));

// Step 4 – Personal Details (optional)
const Step4: React.FC<StepProps> = React.memo(({ formData, setFormData }) => (
  <motion.div
    initial={{ opacity: 0, x: 50 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -50 }}
    className="space-y-6"
  >
    <div className="text-center">
      <UserIcon className="w-16 h-16 text-blue-600 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Tell us about yourself
      </h2>
      <p className="text-gray-600">
        Optional information to better personalize your recommendations
      </p>
    </div>

    <div className="max-w-md mx-auto space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Monthly Income (₹)
        </label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">₹</span>
          <input
            id="monthly-income"
            name="monthly_income"
            type="number"
            value={formData.monthly_income || ''}
            onChange={e => setFormData({ ...formData, monthly_income: Number(e.target.value) || undefined })}
            className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="50,000"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Age
        </label>
        <input
          id="investor-age"
          name="age"
          type="number"
          value={formData.age || ''}
          onChange={e => setFormData({ ...formData, age: Number(e.target.value) || undefined })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="30"
          min="18"
          max="100"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Investment Goals
        </label>
        <textarea
          id="investment-goals"
          name="investment_goals"
          value={formData.investment_goals}
          onChange={e => setFormData({ ...formData, investment_goals: e.target.value })}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent h-24 resize-none"
          placeholder="e.g., Save for retirement, buy a house, children's education..."
        />
      </div>
    </div>
  </motion.div>
));

// Step 5 – Review
const Step5: React.FC<{ formData: FormData }> = React.memo(({ formData }) => (
  <motion.div
    initial={{ opacity: 0, x: 50 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: -50 }}
    className="space-y-6"
  >
    <div className="text-center">
      <CheckCircleIcon className="w-16 h-16 text-green-600 mx-auto mb-4" />
      <h2 className="text-2xl font-bold text-gray-900 mb-2">
        Review Your Profile
      </h2>
      <p className="text-gray-600">
        Please confirm your investment profile details
      </p>
    </div>

    <div className="max-w-2xl mx-auto bg-gray-50 rounded-lg p-6 space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p className="text-sm font-medium text-gray-600">Investment Amount</p>
          <p className="text-lg font-semibold text-gray-900">₹{formData.investment_amount.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-600">Risk Level</p>
          <p className="text-lg font-semibold text-gray-900 capitalize">{formData.risk_level}</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-600">Timeline</p>
          <p className="text-lg font-semibold text-gray-900 capitalize">{formData.timeline}-term</p>
        </div>
        {formData.monthly_income && (
          <div>
            <p className="text-sm font-medium text-gray-600">Monthly Income</p>
            <p className="text-lg font-semibold text-gray-900">₹{formData.monthly_income.toLocaleString()}</p>
          </div>
        )}
      </div>

      {formData.investment_goals && (
        <div>
          <p className="text-sm font-medium text-gray-600">Investment Goals</p>
          <p className="text-gray-900 mt-1">{formData.investment_goals}</p>
        </div>
      )}
    </div>
  </motion.div>
));

const InvestmentProfileOnboarding: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<FormData>({
    investment_amount: 0,
    risk_level: 'medium',
    timeline: 'long',
    investment_goals: '',
    monthly_income: undefined,
    age: undefined,
  });

  const [createProfile, { isLoading }] = useCreateInvestmentProfileMutation();

  const totalSteps = 5;

  const handleNext = () => {
    if (currentStep < totalSteps) setCurrentStep(currentStep + 1);
  };

  const handlePrevious = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleSubmit = async () => {
    try {
      await createProfile(formData).unwrap();
      toast.success('Investment profile created successfully!');
      navigate('/dashboard');
    } catch (error: any) {
      const errorMessage = error?.data?.detail || 'Failed to create investment profile';
      toast.error(errorMessage);
      console.error('Error creating profile:', error);
    }
  };

  const StepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {[1, 2, 3, 4, 5].map(step => (
        <div key={step} className="flex items-center">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${step <= currentStep
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-600'}`}
          >
            {step < currentStep ? <CheckCircleIcon className="w-5 h-5" /> : step}
          </div>
          {step < 5 && (
            <div
              className={`w-12 h-1 mx-2 ${step < currentStep ? 'bg-blue-600' : 'bg-gray-200'}`}
            />
          )}
        </div>
      ))}
    </div>
  );

  const renderStep = () => {
    const stepProps = { formData, setFormData };
    switch (currentStep) {
      case 1:
        return <Step1 {...stepProps} />;
      case 2:
        return <Step2 {...stepProps} />;
      case 3:
        return <Step3 {...stepProps} />;
      case 4:
        return <Step4 {...stepProps} />;
      case 5:
        return <Step5 formData={formData} />;
      default:
        return <Step1 {...stepProps} />;
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return formData.investment_amount > 0;
      case 2:
        return !!formData.risk_level;
      case 3:
        return !!formData.timeline;
      case 4:
        return true; // optional step
      case 5:
        return true;
      default:
        return false;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Set Up Your Investment Profile
          </h1>
          <p className="text-lg text-gray-600">
            Get personalized Indian stock recommendations based on your goals
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          <StepIndicator />

          <div className="min-h-[400px] flex flex-col justify-center">
            <AnimatePresence mode="wait">{renderStep()}</AnimatePresence>
          </div>

          <div className="flex justify-between pt-8 mt-8 border-t border-gray-200">
            <button
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className={`px-6 py-2 rounded-lg font-medium transition-colors ${currentStep === 1
                ? 'text-gray-400 cursor-not-allowed'
                : 'text-gray-600 hover:text-gray-800'}`}
            >
              Previous
            </button>

            {currentStep < totalSteps ? (
              <button
                onClick={handleNext}
                disabled={!canProceed()}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${canProceed()
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={isLoading}
                className="px-6 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Creating Profile...' : 'Complete Setup'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestmentProfileOnboarding;
