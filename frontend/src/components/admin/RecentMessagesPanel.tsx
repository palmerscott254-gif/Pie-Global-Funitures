import React, { useState } from 'react';
import { MessageStatusBadge } from './StatusBadge';
import type { AdminMessage } from '@/types';
import toast from 'react-hot-toast';

interface RecentMessagesPanelProps {
  messages: AdminMessage[];
  loading?: boolean;
  onReply?: (messageId: number, replyText: string) => Promise<void>;
  onResolve?: (messageId: number) => Promise<void>;
}

export const RecentMessagesPanel: React.FC<RecentMessagesPanelProps> = ({
  messages,
  loading = false,
  onReply,
  onResolve,
}) => {
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [replyText, setReplyText] = useState<string>('');
  const [replyingTo, setReplyingTo] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleReply = async () => {
    if (!replyText.trim() || !replyingTo) {
      toast.error('Please enter a reply');
      return;
    }

    setIsSubmitting(true);
    try {
      if (onReply) {
        await onReply(replyingTo, replyText);
        setReplyText('');
        setReplyingTo(null);
      }
    } catch (err) {
      console.error('Reply error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResolve = async (messageId: number) => {
    setIsSubmitting(true);
    try {
      if (onResolve) {
        await onResolve(messageId);
      }
    } catch (err) {
      console.error('Resolve error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Messages</h3>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-20 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Messages</h3>

      {messages.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No messages yet</p>
      ) : (
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="font-semibold text-gray-900">{message.name}</h4>
                    <MessageStatusBadge status={message.status} size="sm" />
                  </div>
                  <p className="text-sm text-gray-600 truncate">{message.email}</p>
                  <p className="text-sm text-gray-700 mt-2 line-clamp-2">{message.message}</p>
                </div>
                <button
                  onClick={() =>
                    setExpandedId(expandedId === message.id ? null : message.id)
                  }
                  className="text-blue-600 hover:text-blue-800 font-medium text-xs whitespace-nowrap"
                >
                  {expandedId === message.id ? 'Hide' : 'View'}
                </button>
              </div>

              {expandedId === message.id && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="bg-gray-50 rounded p-3 mb-4">
                    <p className="text-sm text-gray-700">{message.message}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(message.created_at).toLocaleString()}
                    </p>
                  </div>

                  {message.reply_text && (
                    <div className="bg-blue-50 rounded p-3 mb-4 border border-blue-200">
                      <p className="text-xs font-semibold text-blue-600 mb-1">Your Reply:</p>
                      <p className="text-sm text-gray-700">{message.reply_text}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(message.replied_at || '').toLocaleString()}
                      </p>
                    </div>
                  )}

                  {replyingTo === message.id ? (
                    <div className=" space-y-2">
                      <textarea
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                        placeholder="Type your reply..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={3}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={handleReply}
                          disabled={isSubmitting}
                          className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:bg-gray-400"
                        >
                          {isSubmitting ? 'Sending...' : 'Send Reply'}
                        </button>
                        <button
                          onClick={() => {
                            setReplyingTo(null);
                            setReplyText('');
                          }}
                          disabled={isSubmitting}
                          className="flex-1 bg-gray-200 text-gray-900 py-2 rounded-lg text-sm font-medium hover:bg-gray-300 disabled:bg-gray-400"
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
                            className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
                          >
                            Reply
                          </button>
                          <button
                            onClick={() => handleResolve(message.id)}
                            disabled={isSubmitting}
                            className="flex-1 bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:bg-gray-400"
                          >
                            {isSubmitting ? 'Marking...' : 'Resolve'}
                          </button>
                        </>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
