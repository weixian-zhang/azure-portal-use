from playwright.async_api import Browser, Page, async_playwright, Frame
from typing import Tuple
from dom import DOMManager

class BrowserTarget:
	def __init__(self, targetId: str, type: str, url: str, name: str):
		self.targetId = targetId
		self.type = type
		self.url = url
		self.name = name

class PlaywrightManager:

	def __init__(self):
		self.browser: Browser | None = None
		self.page: Page | None = None
		self.dom_manager = DOMManager()


	async def connect_playwright_to_cdp(self, cdp_url: str = 'http://127.0.0.1:9222') -> bool:
		"""
		Connect Playwright to the same Chrome instance Browser-Use is using.
		This enables custom actions to use Playwright functions.
		"""

		try:
			playwright = await async_playwright().start()
			self.browser = await playwright.chromium.connect_over_cdp(cdp_url)
	

			if self.browser and self.browser.contexts and self.browser.contexts[0].pages:
				self.page = self.browser.contexts[0].pages[0]
			elif self.browser:
				context = await self.browser.new_context()
				self.page = await context.new_page()

			if self.browser and self.page:
				print("Connected to Chrome via Playwright.")
				await self.page.goto('https://portal.azure.com')
				return True

		except Exception as e:
			print(f"❌ Failed to connect Playwright to CDP: {e}")
			return False
		
	

	async def get_all_iframe_dom(self) -> list[str]:

		result = []
		frame_html: list[str] = await self._get_all_iframe_dom()

		for frame in frame_html:
			html = frame
			minified = self.dom_manager.minify_html(html)
			result.append(minified)

		return result


	async def _get_all_iframe_dom(self) -> list[str]:

		result = []

		cdp = await self.page.context.new_cdp_session(self.page)
		
		# Get all frame targets
		targets = await cdp.send('Target.getTargets')
		
		for target in targets['targetInfos']:
			# Process both page and iframe types
			if target['type'] in ['page', 'iframe']:

				# targetId is frameId for iframes
				# using the name targetId here as CDP uses this term for less ambiguity
				target_id = target.get('targetId')

				session_id = await cdp.send('Target.attachToTarget', {
									'targetId': target_id,
									'flatten': True
								})
				session_id = session_id['sessionId']
				
				# await cdp.send('Target.activateTarget', {
				# 					'targetId': target_id,
				# 				})

				await cdp.send('Page.enable', {'session_id': session_id}, )
				await cdp.send('DOM.enable', {'session_id': session_id}, )

				await cdp.send('Page.getFrameTree')
				
				
				root_node = await cdp.send('DOM.getDocument', {
					'depth': -1,
					'pierce': True,
					'session_id': session_id
				})

				node_id = root_node['root']['nodeId']
				backendNodeId = root_node['root']['backendNodeId']

				html = await cdp.send('DOM.getOuterHTML', {
					'nodeId': node_id,
					'backendNodeId': backendNodeId,
					'includeShadowDOM': True
				})

				await cdp.send('Target.detachFromTarget', {
									'sessionId': session_id,
									'targetId': target_id
								})

				if html.get('outerHTML'):
					result.append(html['outerHTML'])


		return result


		# if not targets:
		# 	return ''
		
		# result=[]
		# for t in targets:
		# 	if t.type != 'iframe':
		# 		continue

		# 	frame = self.page.frame(name=t.name)

		# 	if frame:
		# 		html = frame.inner_html()
		# 		result.append(html)
		# return result


async def snapshot_accessibility_tree_for_all_iframes(self) -> dict:
		'''
		Capture accessibility trees from all iframes in the current page using CDP.
		Returns a dictionary with accessibility trees for each frame.
		'''
		
		results = {}
		
		try:
			# Create CDP session
			cdp = await self.page.context.new_cdp_session(self.page)
			
			# Get all frame targets
			targets = await cdp.send('Target.getTargets')
			
			for target in targets['targetInfos']:
				# Process both page and iframe types
				if target['type'] in ['page', 'iframe']:
					try:
						# targetId is frameId for iframes
						# using the name targetId here as CDP uses this term for less ambiguity
						targetId = target.get('targetId')
						frame_url = target.get('url', 'about:blank')

						# testing only
						# if 'sandbox-1' not in frame_url:
						# 	continue

						# Skip empty frames if desired
						if frame_url == 'about:blank':
							continue

						frame_name = target.get('title') or f"frame_{targetId[:8]}"

						print(f"Capturing accessibility tree for: {frame_name} ({frame_url})")
						
						# Attach to the target
						session_id = await cdp.send('Target.attachToTarget', {
							'targetId': targetId,
							'flatten': False
						})

						frame_tree = await cdp.send('Page.getFrameTree', {})

						# no frame found in target
						if (not frame_tree.get('frameTree') and
							not frame_tree.get('frameTree').get('frame') and
							not frame_tree['frameTree']['frame'].get('id')):
							print(f"⚠ Could not get frame ID for target {targetId}, skipping.")
							continue

						frame_id = frame_tree['frameTree']['frame']['id']

						# Enable Accessibility domain for this target
						# await cdp.send('Accessibility.enable', {})
						
						# Get the full accessibility tree
						ax_tree = await cdp.send('Accessibility.getFullAXTree', {
							'depth': 100,
							'frameId': frame_id
						})
						
						results[frame_name] = {
							'url': frame_url,
							'targetId': targetId,
							'type': target['type'],
							'tree': ax_tree.get('nodes', [])
						}
						
						print(f"✓ Captured {frame_name} - {len(ax_tree.get('nodes', []))} nodes")
						
						# Disable and detach

						# await cdp.send('Accessibility.disable', {})
						await cdp.send('Target.detachFromTarget', {
							'sessionId': session_id['sessionId'],
							'targetId': targetId
						})
						

					except Exception as e:
						print(f"✗ Failed to capture {frame_name}: {e}")
						results[f"error_{targetId[:8]}"] = {
							'url': frame_url,
							'error': str(e)
						}
			
			await cdp.detach()
			
		except Exception as e:
			print(f"❌ CDP session error: {e}")
			results['cdp_error'] = {'error': str(e)}
		
		
		return results

	# async def get_browser_targets(self) -> list:

	# 	result = []
	# 	# Create CDP session
	# 	cdp = await self.page.context.new_cdp_session(self.page)
		
	# 	# Get all frame targets
	# 	targets = await cdp.send('Target.getTargets')
		
	# 	for target in targets['targetInfos']:
	# 		# Process both page and iframe types
	# 		if target['type'] in ['page', 'iframe']:
	# 			try:
	# 				# targetId is frameId for iframes
	# 				# using the name targetId here as CDP uses this term for less ambiguity
	# 				targetId = target.get('targetId')
	# 				type = target.get('type')
	# 				name = target.get('title')
	# 				url = target.get('url', 'about:blank')

	# 				result.append(BrowserTarget(targetId, type, url, name))

	# 			except Exception as e:
	# 				print(f"✗ Failed to get target info for {targetId}: {e}")

	# 	return result