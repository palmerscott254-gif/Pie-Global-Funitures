import { useEffect, useState } from 'react';
import { aboutApi } from '@/services/api';
import type { AboutPage as AboutPageType } from '@/types';

const AboutPage = () => {
  const [about, setAbout] = useState<AboutPageType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAbout = async () => {
      try {
        const data = await aboutApi.get();
        setAbout(data);
      } catch (error) {
        console.error('Error fetching about page:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAbout();
  }, []);

  if (loading) {
    return (
      <div className="container-custom py-12 text-center">
        <div className="spinner mx-auto"></div>
      </div>
    );
  }

  if (!about) {
    return (
      <div className="container-custom py-12">
        <h1 className="section-title">About Us</h1>
        <div className="max-w-4xl mx-auto">
          <p className="text-center text-gray-600">About page content will be available soon.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-custom py-12">
      <h1 className="section-title">{about.headline || 'About Us'}</h1>
      <div className="max-w-4xl mx-auto space-y-8">
        {about.body && (
          <div className="prose prose-lg max-w-none">
            <p className="text-gray-700 whitespace-pre-line">{about.body}</p>
          </div>
        )}

        {about.mission && (
          <div className="bg-primary-50 p-6 rounded-lg">
            <h2 className="text-2xl font-bold text-primary-800 mb-4">Our Mission</h2>
            <p className="text-gray-700 whitespace-pre-line">{about.mission}</p>
          </div>
        )}

        {about.vision && (
          <div className="bg-secondary-50 p-6 rounded-lg">
            <h2 className="text-2xl font-bold text-secondary-800 mb-4">Our Vision</h2>
            <p className="text-gray-700 whitespace-pre-line">{about.vision}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AboutPage;
