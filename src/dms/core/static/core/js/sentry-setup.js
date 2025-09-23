const script = document.querySelector("[data-sentry-dsn]");

Sentry.init({
  dsn: script.getAttribute("data-sentry-dsn"),
  environment: location.origin + "-browser",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.feedbackIntegration({
      colorScheme: "system",
    }),
  ],
  tracesSampleRate: 0.2,
  // beforeSend(event, hint) {
  //   if (event.exception && event.event_id) {
  //     Sentry.showReportDialog({ eventId: event.event_id });
  //   }
  //   return event;
  // },
});
