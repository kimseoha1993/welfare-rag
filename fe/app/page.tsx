"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { chat, type Source } from "@/lib/api";

type Message =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string; sources: Source[] }
  | { role: "error"; content: string };

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const query = input.trim();
    if (!query || loading) return;

    setMessages((m) => [...m, { role: "user", content: query }]);
    setInput("");
    setLoading(true);

    try {
      const res = await chat(query);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setMessages((m) => [
        ...m,
        { role: "error", content: `요청 실패: ${msg}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col p-4">
      <header className="py-4">
        <h1 className="text-2xl font-semibold">복지 RAG 챗봇</h1>
        <p className="text-sm text-muted-foreground">
          복지로 데이터 기반으로 답변합니다. (MVP - 샘플 8건)
        </p>
      </header>

      <ScrollArea
        ref={scrollRef}
        className="flex-1 rounded-md border bg-muted/30 p-3"
      >
        <div className="space-y-3">
          {messages.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">
              예) &ldquo;만 65세 어머니가 받을 수 있는 연금?&rdquo;,
              &ldquo;청년 월세 지원 조건&rdquo;
            </p>
          )}
          {messages.map((m, i) => (
            <MessageBubble key={i} message={m} />
          ))}
          {loading && (
            <div className="text-sm text-muted-foreground">생각하는 중…</div>
          )}
        </div>
      </ScrollArea>

      <form onSubmit={onSubmit} className="mt-3 flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="복지 서비스에 대해 물어보세요"
          disabled={loading}
          autoFocus
        />
        <Button type="submit" disabled={loading || !input.trim()}>
          전송
        </Button>
      </form>
    </main>
  );
}

function MessageBubble({ message }: { message: Message }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground">
          {message.content}
        </div>
      </div>
    );
  }
  if (message.role === "error") {
    return (
      <div className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
        {message.content}
      </div>
    );
  }
  return (
    <div className="space-y-2">
      <Card>
        <CardContent className="whitespace-pre-wrap p-3 text-sm">
          {message.content}
        </CardContent>
      </Card>
      {message.sources.length > 0 && (
        <div className="space-y-1 pl-1 text-xs text-muted-foreground">
          <div className="font-medium">출처</div>
          <ul className="space-y-0.5">
            {message.sources.map((s, i) => (
              <li key={i}>
                <a
                  href={s.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline"
                >
                  [{s.distance.toFixed(2)}] {s.service_name}
                </a>
                <span className="ml-1">· {s.source}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
