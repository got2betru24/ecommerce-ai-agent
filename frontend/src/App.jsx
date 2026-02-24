import { useState, useRef, useEffect } from "react";
import {
  Box,
  TextField,
  IconButton,
  Typography,
  Paper,
  CircularProgress,
  Fade,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// Alpine-inspired theme: deep navy, ice blue, crisp white
const theme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      main: "#7BB8D4",      // ice blue
      light: "#A8D4E8",
      dark: "#4A8FAD",
    },
    background: {
      default: "#0A0F1E",   // deep midnight navy
      paper: "#111827",     // slightly lighter navy
    },
    text: {
      primary: "#E8F4F8",   // cool white
      secondary: "#7BB8D4", // ice blue
    },
  },
  typography: {
    fontFamily: "'DM Sans', sans-serif",
    h6: {
      fontFamily: "'DM Serif Display', serif",
      letterSpacing: "0.05em",
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          border: "1px solid rgba(123, 184, 212, 0.12)",
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            "& fieldset": {
              borderColor: "rgba(123, 184, 212, 0.2)",
            },
            "&:hover fieldset": {
              borderColor: "rgba(123, 184, 212, 0.4)",
            },
            "&.Mui-focused fieldset": {
              borderColor: "#7BB8D4",
            },
          },
        },
      },
    },
  },
});

// Individual message bubble
function Message({ message }) {
  const isUser = message.role === "user";

  return (
    <Fade in timeout={300}>
      <Box
        sx={{
          display: "flex",
          justifyContent: isUser ? "flex-end" : "flex-start",
          mb: 2,
        }}
      >
        {/* Assistant avatar */}
        {!isUser && (
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: "linear-gradient(135deg, #4A8FAD, #7BB8D4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              mr: 1.5,
              mt: 0.5,
              flexShrink: 0,
              fontSize: "14px",
            }}
          >
            ⛰
          </Box>
        )}

        <Box
          sx={{
            maxWidth: "70%",
            px: 2,
            py: 1.5,
            borderRadius: isUser
              ? "18px 18px 4px 18px"
              : "18px 18px 18px 4px",
            background: isUser
              ? "linear-gradient(135deg, #4A8FAD, #7BB8D4)"
              : "rgba(123, 184, 212, 0.08)",
            border: isUser
              ? "none"
              : "1px solid rgba(123, 184, 212, 0.15)",
            backdropFilter: "blur(8px)",
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: isUser ? "#0A0F1E" : "#E8F4F8",
              lineHeight: 1.6,
              whiteSpace: "pre-wrap",
              fontWeight: isUser ? 500 : 400,
            }}
          >
            {message.content}
            {/* Blinking cursor while streaming */}
            {message.streaming && (
              <Box
                component="span"
                sx={{
                  display: "inline-block",
                  width: "2px",
                  height: "14px",
                  backgroundColor: "#7BB8D4",
                  ml: 0.5,
                  verticalAlign: "middle",
                  animation: "blink 1s step-end infinite",
                  "@keyframes blink": {
                    "0%, 100%": { opacity: 1 },
                    "50%": { opacity: 0 },
                  },
                }}
              />
            )}
          </Typography>
        </Box>
      </Box>
    </Fade>
  );
}

// Typing indicator while waiting for first chunk
function TypingIndicator() {
  return (
    <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
      <Box
        sx={{
          width: 32,
          height: 32,
          borderRadius: "50%",
          background: "linear-gradient(135deg, #4A8FAD, #7BB8D4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          mr: 1.5,
          fontSize: "14px",
        }}
      >
        ⛰
      </Box>
      <Box
        sx={{
          px: 2,
          py: 1.5,
          borderRadius: "18px 18px 18px 4px",
          background: "rgba(123, 184, 212, 0.08)",
          border: "1px solid rgba(123, 184, 212, 0.15)",
          display: "flex",
          gap: 0.5,
          alignItems: "center",
        }}
      >
        {[0, 1, 2].map((i) => (
          <Box
            key={i}
            sx={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              backgroundColor: "#7BB8D4",
              animation: "bounce 1.2s ease-in-out infinite",
              animationDelay: `${i * 0.2}s`,
              "@keyframes bounce": {
                "0%, 80%, 100%": { transform: "scale(0.6)", opacity: 0.4 },
                "40%": { transform: "scale(1)", opacity: 1 },
              },
            }}
          />
        ))}
      </Box>
    </Box>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm your e-commerce assistant. I can help you look up orders or check product availability. How can I help you today?",
      streaming: false,
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading || isStreaming) return;

    const userMessage = input.trim();
    setInput("");

    // Add user message immediately
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        role: "user",
        content: userMessage,
        streaming: false,
      },
    ]);

    setIsLoading(true);

    try {
      // POST to backend streaming endpoint
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId,
        }),
      });

      if (!response.ok) throw new Error("Request failed");

      // Create a placeholder assistant message to stream into
      const assistantMsgId = (Date.now() + 1).toString();
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMsgId,
          role: "assistant",
          content: "",
          streaming: true,
        },
      ]);

      setIsLoading(false);
      setIsStreaming(true);

      // Read the SSE stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop(); // Keep incomplete line in buffer

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;

          try {
            const event = JSON.parse(line.slice(6)); // Strip "data: "

            if (event.type === "chunk") {
              // Append chunk to the streaming message
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId
                    ? { ...msg, content: msg.content + event.text }
                    : msg
                )
              );
            } else if (event.type === "done") {
              // Store session ID for conversation continuity
              setSessionId(event.session_id);
              // Mark message as done streaming
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMsgId
                    ? { ...msg, streaming: false }
                    : msg
                )
              );
            } else if (event.type === "error") {
              throw new Error(event.message);
            }
          } catch (e) {
            console.error("Failed to parse SSE event:", e);
          }
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          streaming: false,
        },
      ]);
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      {/* Google Fonts */}
      <link
        href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Serif+Display&display=swap"
        rel="stylesheet"
      />

      {/* Subtle background texture */}
      <Box
        sx={{
          minHeight: "100vh",
          background: `
            radial-gradient(ellipse at 20% 50%, rgba(74, 143, 173, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(123, 184, 212, 0.05) 0%, transparent 40%),
            #0A0F1E
          `,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: 2,
        }}
      >
        <Paper
          elevation={0}
          sx={{
            width: "100%",
            maxWidth: 680,
            height: "85vh",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            background: "rgba(17, 24, 39, 0.8)",
            backdropFilter: "blur(20px)",
          }}
        >
          {/* Header */}
          <Box
            sx={{
              px: 3,
              py: 2.5,
              borderBottom: "1px solid rgba(123, 184, 212, 0.12)",
              background: "rgba(123, 184, 212, 0.04)",
            }}
          >
            <Typography variant="h6" sx={{ color: "#E8F4F8" }}>
              Alpine Support
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.75, mt: 0.25 }}>
              <Box
                sx={{
                  width: 7,
                  height: 7,
                  borderRadius: "50%",
                  backgroundColor: "#4CAF50",
                  boxShadow: "0 0 6px #4CAF50",
                }}
              />
              <Typography variant="caption" sx={{ color: "#7BB8D4" }}>
                Online — Orders & Products
              </Typography>
            </Box>
          </Box>

          {/* Messages */}
          <Box
            sx={{
              flex: 1,
              overflowY: "auto",
              px: 3,
              py: 2,
              "&::-webkit-scrollbar": { width: "4px" },
              "&::-webkit-scrollbar-track": { background: "transparent" },
              "&::-webkit-scrollbar-thumb": {
                background: "rgba(123, 184, 212, 0.2)",
                borderRadius: "4px",
              },
            }}
          >
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </Box>

          {/* Input area */}
          <Box
            sx={{
              px: 3,
              py: 2,
              borderTop: "1px solid rgba(123, 184, 212, 0.12)",
              background: "rgba(123, 184, 212, 0.02)",
              display: "flex",
              gap: 1.5,
              alignItems: "flex-end",
            }}
          >
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask about your orders or products..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading || isStreaming}
              size="small"
              sx={{
                "& .MuiInputBase-root": {
                  color: "#E8F4F8",
                  fontSize: "0.9rem",
                },
                "& .MuiInputBase-input::placeholder": {
                  color: "rgba(123, 184, 212, 0.4)",
                  opacity: 1,
                },
              }}
            />
            <IconButton
              onClick={sendMessage}
              disabled={!input.trim() || isLoading || isStreaming}
              sx={{
                background: "linear-gradient(135deg, #4A8FAD, #7BB8D4)",
                color: "#0A0F1E",
                width: 42,
                height: 42,
                flexShrink: 0,
                "&:hover": {
                  background: "linear-gradient(135deg, #5A9FBD, #8BC8E4)",
                },
                "&:disabled": {
                  background: "rgba(123, 184, 212, 0.15)",
                  color: "rgba(123, 184, 212, 0.3)",
                },
                transition: "all 0.2s ease",
              }}
            >
              {isLoading ? (
                <CircularProgress size={18} sx={{ color: "rgba(123, 184, 212, 0.5)" }} />
              ) : (
                <SendIcon sx={{ fontSize: 18 }} />
              )}
            </IconButton>
          </Box>
        </Paper>
      </Box>
    </ThemeProvider>
  );
}