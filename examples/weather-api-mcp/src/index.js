#!/usr/bin/env node

/**
 * Weather API MCP Server
 *
 * A local MCP server demonstrating external API integration with caching.
 * Provides weather information using OpenWeatherMap API.
 *
 * Features:
 * - Current weather lookup by city
 * - 5-day forecast
 * - Air quality information
 * - Response caching (reduces API calls)
 * - Graceful fallback on errors
 *
 * Tools:
 * - get_current_weather: Get current weather for a city
 * - get_forecast: Get 5-day forecast
 * - get_air_quality: Get air quality index
 *
 * Resources:
 * - weather://cache: View cached weather data
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import https from 'https';
import { config } from 'dotenv';

config();

const API_KEY = process.env.OPENWEATHER_API_KEY || 'demo';
const CACHE_TTL = 10 * 60 * 1000; // 10 minutes
const cache = new Map();

/**
 * Make HTTPS request with promise wrapper
 */
function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            resolve(JSON.parse(data));
          } catch (error) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    }).on('error', reject);
  });
}

/**
 * Get data from cache or fetch fresh
 */
async function getCachedOrFetch(cacheKey, fetcher) {
  const cached = cache.get(cacheKey);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    console.error(`[Cache HIT] ${cacheKey}`);
    return { data: cached.data, fromCache: true };
  }

  console.error(`[Cache MISS] ${cacheKey}`);

  try {
    const data = await fetcher();
    cache.set(cacheKey, { data, timestamp: Date.now() });
    return { data, fromCache: false };
  } catch (error) {
    // If fetch fails but we have stale cache, use it
    if (cached) {
      console.error(`[Cache STALE] Using expired cache for ${cacheKey}`);
      return { data: cached.data, fromCache: true, stale: true };
    }
    throw error;
  }
}

/**
 * Fetch current weather from OpenWeatherMap
 */
async function fetchCurrentWeather(city) {
  const url = `https://api.openweathermap.org/data/2.5/weather?q=${encodeURIComponent(city)}&appid=${API_KEY}&units=metric`;
  return await httpsGet(url);
}

/**
 * Fetch 5-day forecast
 */
async function fetchForecast(city) {
  const url = `https://api.openweathermap.org/data/2.5/forecast?q=${encodeURIComponent(city)}&appid=${API_KEY}&units=metric`;
  return await httpsGet(url);
}

/**
 * Fetch air quality data
 */
async function fetchAirQuality(lat, lon) {
  const url = `https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${API_KEY}`;
  return await httpsGet(url);
}

/**
 * Format weather data for human reading
 */
function formatWeatherData(data, fromCache = false) {
  const cacheNote = fromCache ? ' (from cache)' : '';

  return `
**Weather in ${data.name}, ${data.sys.country}**${cacheNote}

🌡️  **Temperature**: ${data.main.temp}°C (feels like ${data.main.feels_like}°C)
🌤️  **Conditions**: ${data.weather[0].description}
💧 **Humidity**: ${data.main.humidity}%
💨 **Wind**: ${data.wind.speed} m/s
☁️  **Cloudiness**: ${data.clouds.all}%
👁️  **Visibility**: ${(data.visibility / 1000).toFixed(1)} km

**Additional Info**:
- Pressure: ${data.main.pressure} hPa
- Min/Max: ${data.main.temp_min}°C / ${data.main.temp_max}°C
- Sunrise: ${new Date(data.sys.sunrise * 1000).toLocaleTimeString()}
- Sunset: ${new Date(data.sys.sunset * 1000).toLocaleTimeString()}
`.trim();
}

/**
 * Format forecast data
 */
function formatForecastData(data, fromCache = false) {
  const cacheNote = fromCache ? ' (from cache)' : '';

  let result = `**5-Day Forecast for ${data.city.name}, ${data.city.country}**${cacheNote}\n\n`;

  // Group by day
  const days = new Map();

  data.list.forEach((item) => {
    const date = new Date(item.dt * 1000);
    const dayKey = date.toDateString();

    if (!days.has(dayKey)) {
      days.set(dayKey, []);
    }

    days.get(dayKey).push(item);
  });

  // Format each day
  for (const [dayKey, items] of days) {
    const date = new Date(dayKey);
    result += `\n📅 **${date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}**\n`;

    // Get min/max temps for the day
    const temps = items.map(i => i.main.temp);
    const minTemp = Math.min(...temps);
    const maxTemp = Math.max(...temps);

    // Get most common weather condition
    const conditions = items.map(i => i.weather[0].description);
    const mostCommon = conditions.sort((a, b) =>
      conditions.filter(c => c === a).length - conditions.filter(c => c === b).length
    ).pop();

    result += `   ${mostCommon} | ${minTemp.toFixed(1)}°C - ${maxTemp.toFixed(1)}°C\n`;
  }

  return result;
}

/**
 * Format air quality data
 */
function formatAirQualityData(data, fromCache = false) {
  const cacheNote = fromCache ? ' (from cache)' : '';
  const aqi = data.list[0].main.aqi;

  const qualityLevels = {
    1: '✅ Good',
    2: '🟢 Fair',
    3: '🟡 Moderate',
    4: '🟠 Poor',
    5: '🔴 Very Poor'
  };

  const components = data.list[0].components;

  return `
**Air Quality**${cacheNote}

**Overall AQI**: ${qualityLevels[aqi] || aqi}

**Components** (μg/m³):
- CO (Carbon Monoxide): ${components.co.toFixed(2)}
- NO₂ (Nitrogen Dioxide): ${components.no2.toFixed(2)}
- O₃ (Ozone): ${components.o3.toFixed(2)}
- PM2.5 (Fine Particles): ${components.pm2_5.toFixed(2)}
- PM10 (Coarse Particles): ${components.pm10.toFixed(2)}
- SO₂ (Sulfur Dioxide): ${components.so2.toFixed(2)}
`.trim();
}

async function main() {
  console.error('🌤️  Starting Weather API MCP Server...');

  if (API_KEY === 'demo') {
    console.error('⚠️  WARNING: Using demo API key. Set OPENWEATHER_API_KEY environment variable for production use.');
  }

  const server = new Server(
    {
      name: 'weather-api-mcp',
      version: '1.0.0'
    },
    {
      capabilities: {
        tools: {},
        resources: {}
      }
    }
  );

  // ==========================================================================
  // TOOL: get_current_weather
  // ==========================================================================

  server.tool(
    'get_current_weather',
    'Get current weather conditions for a city',
    {
      type: 'object',
      properties: {
        city: {
          type: 'string',
          description: 'City name (e.g., "London", "New York", "Tokyo")'
        }
      },
      required: ['city']
    },
    async ({ city }) => {
      try {
        console.error(`[Tool] get_current_weather: ${city}`);

        const cacheKey = `weather:${city.toLowerCase()}`;
        const { data, fromCache, stale } = await getCachedOrFetch(
          cacheKey,
          () => fetchCurrentWeather(city)
        );

        const formatted = formatWeatherData(data, fromCache || stale);

        return {
          content: [{
            type: 'text',
            text: formatted
          }]
        };
      } catch (error) {
        console.error(`[Error] get_current_weather: ${error.message}`);

        return {
          content: [{
            type: 'text',
            text: `❌ Failed to get weather data: ${error.message}\n\nPlease check:\n- City name is correct\n- API key is valid\n- Internet connection is working`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: get_forecast
  // ==========================================================================

  server.tool(
    'get_forecast',
    'Get 5-day weather forecast for a city',
    {
      type: 'object',
      properties: {
        city: {
          type: 'string',
          description: 'City name (e.g., "London", "New York", "Tokyo")'
        }
      },
      required: ['city']
    },
    async ({ city }) => {
      try {
        console.error(`[Tool] get_forecast: ${city}`);

        const cacheKey = `forecast:${city.toLowerCase()}`;
        const { data, fromCache, stale } = await getCachedOrFetch(
          cacheKey,
          () => fetchForecast(city)
        );

        const formatted = formatForecastData(data, fromCache || stale);

        return {
          content: [{
            type: 'text',
            text: formatted
          }]
        };
      } catch (error) {
        console.error(`[Error] get_forecast: ${error.message}`);

        return {
          content: [{
            type: 'text',
            text: `❌ Failed to get forecast data: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: get_air_quality
  // ==========================================================================

  server.tool(
    'get_air_quality',
    'Get air quality information for a city',
    {
      type: 'object',
      properties: {
        city: {
          type: 'string',
          description: 'City name (e.g., "London", "New York", "Tokyo")'
        }
      },
      required: ['city']
    },
    async ({ city }) => {
      try {
        console.error(`[Tool] get_air_quality: ${city}`);

        // First get coordinates from weather API
        const cacheKey = `weather:${city.toLowerCase()}`;
        const { data: weatherData } = await getCachedOrFetch(
          cacheKey,
          () => fetchCurrentWeather(city)
        );

        const { lat, lon } = weatherData.coord;

        // Then get air quality
        const aqCacheKey = `airquality:${lat}:${lon}`;
        const { data: aqData, fromCache, stale } = await getCachedOrFetch(
          aqCacheKey,
          () => fetchAirQuality(lat, lon)
        );

        const formatted = formatAirQualityData(aqData, fromCache || stale);

        return {
          content: [{
            type: 'text',
            text: formatted
          }]
        };
      } catch (error) {
        console.error(`[Error] get_air_quality: ${error.message}`);

        return {
          content: [{
            type: 'text',
            text: `❌ Failed to get air quality data: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // RESOURCE: weather://cache
  // ==========================================================================

  server.resource(
    'weather://cache',
    'View cached weather data',
    async () => {
      console.error('[Resource] weather://cache');

      if (cache.size === 0) {
        return {
          contents: [{
            uri: 'weather://cache',
            mimeType: 'text/plain',
            text: 'No cached data available'
          }]
        };
      }

      let text = '**Cached Weather Data**\n\n';

      for (const [key, value] of cache.entries()) {
        const age = Math.floor((Date.now() - value.timestamp) / 1000);
        const expired = age > (CACHE_TTL / 1000);

        text += `- **${key}**: ${expired ? '🔴 expired' : '🟢 valid'} (${age}s old)\n`;
      }

      text += `\n**Cache Settings**:\n- TTL: ${CACHE_TTL / 1000}s\n- Entries: ${cache.size}`;

      return {
        contents: [{
          uri: 'weather://cache',
          mimeType: 'text/plain',
          text
        }]
      };
    }
  );

  // ==========================================================================
  // START SERVER
  // ==========================================================================

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('✅ Weather API MCP Server ready');
  console.error('📍 Registered tools: get_current_weather, get_forecast, get_air_quality');
  console.error('📍 Registered resources: weather://cache');
}

main().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
