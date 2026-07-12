FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /App

COPY . .
RUN dotnet restore "Poe2scout.ItemSync.Worker/Poe2scout.ItemSync.Worker.csproj"
RUN dotnet publish "Poe2scout.ItemSync.Worker/Poe2scout.ItemSync.Worker.csproj" \
    -c Release \
    -o out \
    --no-restore \
    /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/runtime:10.0 AS final
WORKDIR /App
COPY --from=build /App/out .
ENTRYPOINT ["dotnet", "Poe2scout.ItemSync.Worker.dll"]