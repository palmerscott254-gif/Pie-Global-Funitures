import { motion } from 'framer-motion';
import { FaMapMarkerAlt, FaClock, FaPhone, FaEnvelope, FaDirections } from 'react-icons/fa';

const LocationSection = () => {
  const locationData = {
    address: 'Kayole Spine Rd, Nairobi',
    phone: '+254 704 456 788',
    email: 'muthikej392@gmail.com',
    hours: [
      { day: 'Monday - Friday', time: '8:00 AM - 6:00 PM' },
      { day: 'Saturday', time: '9:00 AM - 4:00 PM' },
      { day: 'Sunday', time: 'Closed' },
    ],
    googleMapsUrl: 'https://maps.app.goo.gl/TVPH1DHdm4jCRJ4A7?g_st=ac',
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
      },
    },
  };

  return (
    <section className="relative py-20 overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50">
        <div className="absolute top-0 left-0 w-96 h-96 bg-primary-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-secondary-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000" />
        <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000" />
      </div>

      <div className="container-custom relative z-10">
        {/* Section Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <motion.h2
            className="text-4xl md:text-5xl font-bold mb-4"
            animate={{
              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: 'linear',
            }}
            style={{
              backgroundImage: 'linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899, #3b82f6)',
              backgroundSize: '200% auto',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Visit Pie Global Furniture
          </motion.h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Experience our showroom and discover the perfect pieces for your space
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          {/* Address Card */}
          <motion.div
            variants={itemVariants}
            className="group relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-white/20"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/10 to-secondary-500/10 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <FaMapMarkerAlt className="text-3xl text-white" />
              </div>

              <h3 className="text-2xl font-bold mb-4 text-gray-800">Our Location</h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                {locationData.address}
              </p>

              <a
                href={locationData.googleMapsUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-full font-semibold hover:shadow-lg hover:scale-105 transition-all duration-300"
              >
                <FaDirections />
                Get Directions
              </a>
            </div>
          </motion.div>

          {/* Hours Card */}
          <motion.div
            variants={itemVariants}
            className="group relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-white/20"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-secondary-500/10 to-pink-500/10 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-secondary-500 to-pink-500 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <FaClock className="text-3xl text-white" />
              </div>

              <h3 className="text-2xl font-bold mb-4 text-gray-800">Opening Hours</h3>
              <div className="space-y-3">
                {locationData.hours.map((schedule, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-gray-700 font-medium">{schedule.day}</span>
                    <span className="text-gray-600">{schedule.time}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Contact Card */}
          <motion.div
            variants={itemVariants}
            className="group relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-white/20"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-pink-500/10 to-primary-500/10 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-pink-500 to-primary-500 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <FaPhone className="text-3xl text-white" />
              </div>

              <h3 className="text-2xl font-bold mb-6 text-gray-800">Contact Us</h3>
              
              <div className="space-y-4">
                <a
                  href={`tel:${locationData.phone}`}
                  className="flex items-center gap-3 text-gray-700 hover:text-primary-600 transition-colors group/link"
                >
                  <FaPhone className="text-primary-600 group-hover/link:scale-110 transition-transform" />
                  <span>{locationData.phone}</span>
                </a>

                <a
                  href={`mailto:${locationData.email}`}
                  className="flex items-center gap-3 text-gray-700 hover:text-primary-600 transition-colors group/link"
                >
                  <FaEnvelope className="text-primary-600 group-hover/link:scale-110 transition-transform" />
                  <span>{locationData.email}</span>
                </a>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  Have questions? We're here to help you find the perfect furniture for your space.
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default LocationSection;
