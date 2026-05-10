import React, { useState } from 'react';
import { MessageStatusBadge } from './StatusBadge';
import { useAdminMessages } from '@/hooks';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import toast from 'react-hot-toast';

export const MessagesManagement: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const [replyText, setReplyText] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { messages, loading, error, reply, resolve, refetch } = useAdminMessages(
    true,
    10000,
    100
  );

  const filteredMessages = statusFilter
    ? messages.filter((m) => m.status === statusFilter)
    : messages;

  const handleReply = async (messageId: number) => {
    if (!replyText.trim()) {
      toast.error('Please enter a reply');
      return;
    }

    setIsSubmitting(true);
    try {
      await reply(messageId, replyText, 'replied');
      setReplyText('');
      setReplyingTo(null);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResolve = async (messageId: number) => {
    setIsSubmitting(true);
    try {
      await resolve(messageId);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading && !messages.length) {
    return <LoadingSpinner fullScreen />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        <p className="font-medium">Error loading messages: {error}</p>
        <button
          onClick={refetch}
          className="mt-2 text-red-600 hover:text-red-700 font-medium underline"
        >
          Try Again
        </button>
      </div>
    );
  }

  const statusOptions = [
    { value: 'new', label: 'New' },
    { value: 'read', label: 'Read' },
    { value: 'replied', label: 'Replied' },
    { value: 'resolved', label: 'Resolved' },
  ];

  return (
    <div className="space-y-6">
      {/* Header and Filters */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Messages Management</h2>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setStatusFilter('')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              statusFilter === ''
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All Messages
          </button>
          {statusOptions.map((status) => (
            <button
              key={status.value}
              onClick={() => setStatusFilter(status.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {status.label}
            </button>
          ))}
        </div>
      </div>

      {/* Messages List */}
      <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-200">
        {filteredMessages.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            <p>No messages found</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredMessages.map((message) => (
              <React.Fragment key={message.id}>
                <div className="p-6 hover:bg-gray-50 transition-colors cursor-pointer">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="text-lg font-semibold text-gray-900">{message.name}</h3>
                        <MessageStatusBadge status={message.status} size="sm" />
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>{message.email}</span>
                        {message.phone && <span>{message.phone}</span>}
                        <span>{new Date(message.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <button
                      onClick={() =>
                        setExpandedId(expandedId === message.id ? null : message.id)
                      }
                      className="ml-4 text-blue-600 hover:text-blue-800 font-medium text-sm whitespace-nowrap"
                    >
                      {expandedId === message.id ? 'Hide' : 'View'}
                    </button>
                  </div>

                  {/* Message Preview */}
                  <p className="text-gray-700 line-clamp-2">{message.message}</p>
                </div>

                {/* Expanded Details */}
                {expandedId === message.id && (
                  <div className="bg-gray-50 p-6 space-y-4">
                    {/* Full Message */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Message</h4>
                      <div className="bg-white p-4 rounded border border-gray-200 text-gray-700 whitespace-pre-wrap break-words">
                        {message.message}
                      </div>
                    </div>

                    {/* Reply Section */}
                    {message.reply_text && (
                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Your Reply</h4>
                        <div className="bg-blue-50 p-4 rounded border border-blue-200">
                          <p className="text-gray-700 whitespace-pre-wrap break-words">
                            {message.reply_text}
                          </p>
                          <p className="text-xs text-gray-500 mt-2">
                            Sent on {new Date(message.replied_at || '').toLocaleString()}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Action Buttons */}
                    {replyingTo === message.id ? (
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-900 mb-2">
                            Your Reply
                          </label>
                          <textarea
                            value={replyText}
                            onChange={(e) => setReplyText(e.target.value)}
                            placeholder="Type your reply to the customer..."
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                            rows={4}
                          />
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleReply(message.id)}
                            disabled={isSubmitting}
                            className="flex-1 bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                          >
                            {isSubmitting ? 'Sending...' : 'Send Reply'}
                          </button>
                          <button
                            onClick={() => {
                              setReplyingTo(null);
                              setReplyText('');
                            }}
                            disabled={isSubmitting}
                            className="flex-1 bg-gray-200 text-gray-900 py-2 rounded-lg font-medium hover:bg-gray-300 disabled:bg-gray-400 transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex gap-2">
                        {message.status !== 'resolved' && (
                          <>
                            <button
                              onClick={() => setReplyingTo(message.id)}
                              className="flex-1 bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                            >
                              Reply
                            </button>
                            <button
                              onClick={() => handleResolve(message.id)}
                              disabled={isSubmitting}
                              className="flex-1 bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                            >
                              {isSubmitting ? 'Marking...' : 'Mark Resolved'}
                            </button>
                          </>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
