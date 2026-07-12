FROM mcr.microsoft.com/dotnet/runtime:10.0 AS base
USER $APP_UID
WORKDIR /app

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["net/Poe2scout/Poe2scout/Poe2scout.csproj", "Poe2scout/"]
COPY ["net/Poe2scout/Poe2scout.CurrencyExchange.Worker/Poe2scout.CurrencyExchange.Worker.csproj", "Poe2scout.CurrencyExchange.Worker/"]
RUN dotnet restore "Poe2scout.CurrencyExchange.Worker/Poe2scout.CurrencyExchange.Worker.csproj"
COPY net/Poe2scout .
WORKDIR "/src/Poe2scout.CurrencyExchange.Worker"
RUN dotnet publish "Poe2scout.CurrencyExchange.Worker.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "Poe2scout.CurrencyExchange.Worker.dll"]
